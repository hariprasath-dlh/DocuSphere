import re
from query_normalizer import normalize_query # Matches new architecture

def normalize_intent(query: str) -> dict:
    """
    Normalizes a user query into a canonical intent and target.
    Returns: {'intent': 'LIST_ONLY'|'EXPLAIN'|'GENERAL'|'EXTRACT', 
              'target': 'soft_skills'|'technical_skills'|'projects'|'internship'|'education'|'links'|'email'|'phone'|None}
    """
    # 1. Normalize Query (Spelling + Phrasing)
    q_normalized = normalize_query(query)
    q = q_normalized.lower().strip()
    
    # --- 2. Detect Intent Category ---
    intent = "GENERAL"
    
    # EXTRACTION markers
    extract_markers = ["link", "url", "linkedin", "email", "mail", "phone", "number", "contact"]
    if any(m in q for m in extract_markers):
        intent = "EXTRACT"
    
    # LIST_ONLY keywords 
    list_markers = ["list", "mention", "enumerate", "names", "checklist", "bullet points", "give me", "show me"]
    
    # EXPLAIN keywords 
    explain_markers = ["explain", "describe", "details", "elaborate", "experience with", "history", "background", "summary", "tell me"]
    
    # Specific Intent Overrides
    if intent != "EXTRACT":
        if any(m in q for m in explain_markers):
            intent = "EXPLAIN"
        elif any(m in q for m in list_markers):
            intent = "LIST_ONLY"
        elif q.startswith(("what", "which")):
            intent = "LIST_ONLY"


    # --- 3. Detect Canonical Target ---
    target = None
    
    # Target Clusters (Expanded/Refined)
    targets = {
        "soft_skills": ["soft skills", "strength", "trait", "personality", "capability", "competenc", "interpersonal"],
        "technical_skills": ["technical", "coding", "programming", "language", "framework", "tool", "stack", "technology", "tech skill"],
        "projects": ["project", "capstone", "system", "app", "application", "platform", "website"],
        "internship": ["intern", "experience", "work history", "job", "role", "employment"],
        "education": ["education", "college", "university", "school", "degree", "btech", "academic", "cgpa"],
        "links": ["link", "url", "linkedin", "github", "website"],
        "email": ["email", "mail", "address"],
        "phone": ["phone", "number", "contact", "mobile", "cell"]
    }
    
    # Iterate through targets
    for canonical_target, keywords in targets.items():
        if any(k in q for k in keywords):
            target = canonical_target
            break
            
    # Refinement: Infer intent from target if GENERAL
    if intent == "GENERAL" and target:
        if target in ["internship", "projects", "education"]: 
            # "internship" -> usually implies "tell me about internship"
            intent = "EXPLAIN"
        elif target in ["soft_skills", "technical_skills", "certifications"]:
            # "skills" -> usually implies "list skills"
            intent = "LIST_ONLY"
            
    # Override: "list projects" -> LIST_ONLY
    if target == "projects" and any(m in q for m in list_markers):
        intent = "LIST_ONLY"
        
    # Override: "explain skills" -> EXPLAIN
    if target in ["soft_skills", "technical_skills"] and any(m in q for m in explain_markers):
        intent = "EXPLAIN"

    return {"intent": intent, "target": target}
