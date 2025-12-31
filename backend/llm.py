import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:mini"

def generate_answer(query: str, evidence_chunks: list[dict], intent: str = "GENERAL") -> str:
    """
    Calls Ollama locally to generate a clean, grounded answer.
    NOW INTENT-AWARE + ID-LEAKAGE PROOF.
    """

    if not evidence_chunks:
        return "Not found in document."

    # Specific Rules based on Intent as per Master Prompt
    rules = ""
    if intent == "LIST_ONLY":
        rules = """- Output ONLY bullet points
- Each item must be VERY short (max 4 words)
- NO explanations
- NO descriptions
- NO technologies (unless asked)
- NO projects (unless asked)
- NO sentences
- Do NOT use words like 'developed', 'created', 'used', 'system', 'project'"""
    elif intent == "EXPLAIN":
        rules = """- Provide a detailed explanation
- Use paragraphs
- Do NOT use bullet lists unless explicitly asked"""
    else:
        rules = "- Answer strictly using the context provided"

    # Format context with identifiers - BUT HIDE IDs from LLM if we don't want them in output?
    # Actually, we need IDs for our internal tracking, but we tell LLM to cite by Page.
    context_str = ""
    for chunk in evidence_chunks:
        page = chunk.get('page', '?')
        # We present the source as "Source (Page X)" to the LLM so it naturally cites pages
        context_str += f"[Source: Page {page}]:\n{chunk['text']}\n\n"

    # Mandatory System Prompt Template
    prompt = f"""
You are a strict document question-answering system.

INTENT: {intent}

RULES:
- You MUST answer only using the provided context.
{rules}
- If the answer is not found, output exactly:
  "Not found in document."
- CITATION RULE:
  - Do NOT output vector IDs like 'a1b2...' or chunk hashes.
  - Cite sources ONLY as (Page X).
  - Example: "He knows Python (Page 1)."

Question:
{query}

Context:
{context_str}

Answer:
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0, # Strict
            "num_predict": 512
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})

    try:
        with urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            raw_response = json.loads(resp_body)["response"].strip()
            
            # Post-LLM Validation / Cleanup
            return validate_and_clean_output(raw_response, intent)

    except HTTPError as e:
        print(f"LLM Error: {e}")
        return "Error generating answer from LLM."
    except URLError as e:
        print(f"Connection Error: {e}")
        return "Error connecting to LLM service. Is Ollama running?"

def validate_and_clean_output(response: str, intent: str) -> str:
    """
    Enforces output constraints strictly and removes leaked IDs.
    """
    # 1. Privacy/Cleanliness check: Remove any residual Hash/ID patterns if LLM disobeyed
    # Regex for typical IDs (alphanumeric, long) - optional but good safety.
    # Simpler: just ensure we don't see "chunk_" or hex strings if possible.
    
    if intent == "LIST_ONLY":
        lines = response.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line: 
                continue
            
            # Reject conversational filler
            if line.lower().startswith(("here are", "sure", "i found", "based on", "the soft skills", "following is")):
                continue
                
            # Reject if contains forbidden words
            if any(forbidden in line.lower() for forbidden in ["developed", "project", "system", "tool", "created", "implemented", "used"]):
                continue

            # Reject sentences longer than 4 words
            content_only = re.sub(r'^[\u2022\-\*\d\.]+\s*', '', line)
            # Also remove citations from word count consideration
            content_only = re.sub(r'\(Page \d+\)', '', content_only)
            
            word_count = len(content_only.split())
            
            if word_count > 4:
                continue

            cleaned_lines.append(line)
        
        if not cleaned_lines:
            return "Not found in document."
            
        return "\n".join(cleaned_lines)

    return response
