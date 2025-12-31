import uuid

def chunk_text_with_metadata(pages_data, source="document", chunk_size=300, overlap=50):
    """
    Splits text into chunks while preserving page numbers and source metadata.
    pages_data: list of dicts {'page': int, 'text': str}
    """
    chunks = []

    for page_entry in pages_data:
        text = page_entry["text"]
        page_num = page_entry["page"]
        
        words = text.split()
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            if len(chunk_text) > 20: # Filter very small noise
                chunks.append({
                    "chunk_id": str(uuid.uuid4())[:8],
                    "text": chunk_text,
                    "page": page_num,
                    "source": source
                })

            start = end - overlap

    return chunks

from sentence_transformers import SentenceTransformer

# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks(text_chunks):
    """
    Converts a list of text strings into embeddings (vectors)
    """
    embeddings = embedding_model.encode(text_chunks)
    return embeddings

import faiss
import numpy as np


def create_faiss_index(embeddings):
    """
    Creates a FAISS index from embeddings
    """
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index

def search_faiss(query, index, chunks, top_k=3):
    """
    Search FAISS index using a query string
    """
    # Convert query to embedding
    query_embedding = embedding_model.encode([query])

    # Search FAISS
    distances, indices = index.search(query_embedding, top_k)

    # Fetch matching chunks
    results = []
    
    # Handle case where FAISS returns -1 for empty index or no match
    if len(indices) > 0:
        for idx in indices[0]:
            if idx != -1 and idx < len(chunks):
                results.append(chunks[idx])

    return results

def filter_chunks_by_target(chunks: list[dict], target: str, intent: str) -> list[dict]:
    """
    Filters chunks based on target-aware keywords for high precision.
    If no target matches, returns empty list.
    """
    if not target:
        return chunks

    target_keywords = {
        "soft_skills": ["soft", "skill", "strength", "trait", "personal", "team", "leader", "communicat", "attribute"],
        "technical_skills": ["techn", "program", "code", "lang", "tool", "framework", "software", "stack", "dev"],
        "projects": ["project", "system", "app", "web", "platform", "build", "developed", "created"],
        "internship": ["intern", "experience", "work", "job", "role", "employ", "company"],
        "education": ["edu", "college", "university", "school", "degree", "mark", "grade", "b.tech", "study", "cgpa"],
        "links": ["http", "www", "url", ".com", ".in", "link", "linkedin", "github"],
        "email": ["@", ".com", ".net", "email", "mail"],
        "phone": ["+", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "phone", "contact", "mobile"]
    }

    keywords = target_keywords.get(target, [])
    if not keywords:
        return chunks

    filtered_chunks = []
    for chunk in chunks:
        text = chunk["text"].lower()
        matches_keyword = any(k in text for k in keywords)
        
        if matches_keyword:
            filtered_chunks.append(chunk)
            
    return filtered_chunks
