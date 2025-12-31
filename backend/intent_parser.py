import re

def classify_intent(query: str) -> str:
    """
    Classifies the user's intent based on keywords strictly as per requirements.
    Returns: 'LIST_ONLY', 'EXPLAIN', or 'GENERAL'
    """
    q = query.lower().strip()
    
    # LIST_ONLY keywords
    list_keywords = [
        "only",
        "list",
        "names",
        "what are the soft skills",
        "what skills"
    ]
    
    if any(k in q for k in list_keywords):
        return "LIST_ONLY"
    
    # EXPLAIN keywords
    explain_keywords = [
        "explain",
        "describe",
        "tell me about"
    ]
    
    if any(k in q for k in explain_keywords):
        return "EXPLAIN"
        
    return "GENERAL"

def is_project_query(query: str) -> bool:
    """
    Legacy check for deterministic extraction support.
    Keeps compatibility with previous logic but uses new classification if needed.
    """
    q = query.lower()
    # Check if specifically asking for project names
    return "project" in q and ("name" in q or "list" in q) and classify_intent(q) == "LIST_ONLY"

def extract_project_names_deterministically(chunks: list[dict]) -> str:
    """
    Extracts likely project titles from chunks without using an LLM.
    """
    candidates = set()
    
    for chunk in chunks:
        text = chunk["text"]
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Constraints for a Project Title
            if len(line) < 3 or len(line) > 100:
                continue
                
            keywords = ["System", "App", "Application", "Platform", "Detector", "Tracker", "Builder", "Organizer", "Management", "IoT", "Smart", "Automated"]
            has_keyword = any(k in line for k in keywords)
            
            is_sentence = line.endswith('.') and len(line.split()) > 6
            if is_sentence:
                continue

            if "project" in line.lower() or has_keyword:
                if line.lower() in ["projects", "personal projects", "academic projects", "project details"]:
                    continue
                
                caps_count = sum(1 for c in line if c.isupper())
                if caps_count >= 2 or (len(line.split()) == 1 and caps_count == 1):
                    cleaned = re.sub(r'^[\u2022\-\*\d\.]+\s*', '', line)
                    candidates.add(cleaned)

    if not candidates:
        return "Not found in document."

    return "\n".join(sorted(list(candidates)))
