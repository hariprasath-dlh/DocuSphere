from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
import uuid
import re

from retrieval import (
    chunk_text_with_metadata,
    embed_chunks,
    create_faiss_index,
    search_faiss,
    filter_chunks_by_target
)

from reasoning import decompose_query
from llm import generate_answer
from intent_normalizer import normalize_intent
from query_normalizer import normalize_query
from output_mode import detect_output_mode, extract_urls, extract_emails, extract_phone
from parsers import get_pages_data

app = FastAPI()

# Allow all origins for development convenience
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global in-memory store (Reset every upload)
FAISS_STORE = {
    "index": None,
    "chunks": None,
    "filename": None,
    "upload_id": None
}

class QueryRequest(BaseModel):
    query: str

class EvidenceChunk(BaseModel):
    chunk_id: str
    text: str
    page: int
    source: str

class AnswerResponse(BaseModel):
    original_query: str
    sub_queries: list[str]
    answer: str
    evidence: list[EvidenceChunk]

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain"
}

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global FAISS_STORE
    
    try:
        # 1. Reset Vector Index (Single Document Mode)
        FAISS_STORE = {
            "index": None,
            "chunks": None,
            "filename": None,
            "upload_id": None
        }

        # 2. MIME-Type Validation
        if file.content_type not in ALLOWED_MIME_TYPES:
             return JSONResponse(
                status_code=400,
                content={
                    "status": "error", 
                    "message": f"Unsupported file type: {file.content_type}. Please upload PDF, DOCX, PPTX, XLSX, or TXT."
                }
            )

        contents = await file.read()
        filename = file.filename
        upload_id = uuid.uuid4().hex

        # 3. Parsing (Unified Router)
        try:
            pages_data = get_pages_data(contents, filename)
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"Parsing Error: {str(e)}"}
            )

        if not pages_data:
             return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No extractable text found in document."}
            )

        # 4. Ingestion (Chunks + Embeddings + Index)
        chunks = chunk_text_with_metadata(pages_data, source=filename)
        if not chunks:
             return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Document is too short or empty."}
            )
            
        texts = [c["text"] for c in chunks]
        embeddings = embed_chunks(texts)
        index = create_faiss_index(embeddings)

        # 5. Commit to Store
        FAISS_STORE["index"] = index
        FAISS_STORE["chunks"] = chunks
        FAISS_STORE["filename"] = filename
        FAISS_STORE["upload_id"] = upload_id

        return {
            "status": "success",
            "filename": filename,
            "upload_id": upload_id,
            "pages": len(pages_data),
            "chunks": len(chunks)
        }

    except Exception as e:
        print(f"FATAL Upload Error: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Unexpected system error: {str(e)}"}
        )


@app.post("/query", response_model=AnswerResponse)
def query_document(request: QueryRequest):
    if not FAISS_STORE.get("index"):
        return {
            "original_query": request.query,
            "sub_queries": [],
            "answer": "System is not ready. Please upload a document first.",
            "evidence": []
        }

    raw_query = request.query
    index = FAISS_STORE["index"]
    chunks = FAISS_STORE["chunks"]

    # 1️⃣ Early Query Normalization (ChatGPT-like Robustness)
    # This runs BEFORE routing or retrieval.
    normalized_query = normalize_query(raw_query)
    print(f"DEBUG: Original: {raw_query} -> Normalized: {normalized_query}")

    # 2️⃣ Output Mode Detection (Short-Circuit for Extraction)
    # Refined: We use the intent from intent_normalizer for more robust detection.
    intent_data = normalize_intent(normalized_query)
    intent = intent_data["intent"]
    target = intent_data["target"]
    
    # Retrieve context
    sub_queries = decompose_query(normalized_query)
    all_unique_chunks = {}
    for sub_q in sub_queries:
        retrieved = search_faiss(sub_q, index, chunks)
        for chunk in retrieved:
            all_unique_chunks[chunk["chunk_id"]] = chunk
    context_chunks = list(all_unique_chunks.values())

    # Apply Target-Aware Filtering (Moved to retrieval.py)
    context_chunks = filter_chunks_by_target(context_chunks, target, intent)

    # 3️⃣ Routing Logic
    final_answer = ""
    
    if intent == "EXTRACT":
        # BYPASS LLM
        if target == "links":
            final_answer = extract_urls(context_chunks, normalized_query)
        elif target == "email":
            final_answer = extract_emails(context_chunks)
        elif target == "phone":
            final_answer = extract_phone(context_chunks)
        else:
            # Fallback to semantic if EXTRACT intent but no specific regex target
            final_answer = generate_answer(normalized_query, context_chunks, intent)
    else:
        # Standard Semantic Flow (LLM)
        final_answer = generate_answer(normalized_query, context_chunks, intent)

    # 4️⃣ Format Evidence (Internal IDs hidden by return model)
    formatted_evidence = [
        EvidenceChunk(
            chunk_id=c["chunk_id"],
            text=c["text"],
            page=c["page"],
            source=c["source"]
        )
        for c in context_chunks
    ]

    return {
        "original_query": raw_query,
        "sub_queries": sub_queries,
        "answer": final_answer,
        "evidence": formatted_evidence
    }
