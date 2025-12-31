from rapidfuzz import process, fuzz

def normalize_query(query: str) -> str:
    """
    Normalizes a user query by correcting spelling and standardizing phrasing.
    Uses rapidfuzz for fuzzy matching against a dictionary of known terms.
    """
    q_tokens = query.lower().split()
    normalized_tokens = []
    
    # Dictionary of known terms / phrases
    # Mapping: invalid_or_variant -> canonical
    
    # 1. Phrasing Map (Multi-token phrases handled via simple replacement first)
    # This is a basic approach; for robust multi-token, we might need phrase matching.
    # We'll do string replacement for common phrases first.
    
    phrase_map = {
        "giv details": "explain",
        "tell me about": "explain",
        "what are my": "list my",
        "what are the": "list the",
        "give me": "list",
        "show me": "list",
        "mention": "list",
        "details about": "explain",
        "abt": "about",
        "intrn": "intern",
        "giv": "give",
        "skil": "skill",
    }
    
    # Apply phrase replacements
    q_normalized_phrasing = query.lower()
    for phrase, canonical in phrase_map.items():
        if phrase in q_normalized_phrasing:
            q_normalized_phrasing = q_normalized_phrasing.replace(phrase, canonical)
            
    # 2. Spelling Correction (Token-level)
    # Helper dictionary for fuzzy matching targets
    known_terms = [
        "skills", "soft", "technical", "projects", "internship", "experience", 
        "education", "strength", "weakness", "details", "explain", "list", 
        "system", "application", "resume", "cv", "job", "work", "history"
    ]
    
    tokens = q_normalized_phrasing.split()
    
    for token in tokens:
        # Ignore short words or numbers
        if len(token) < 3 or token.isdigit():
            normalized_tokens.append(token)
            continue
            
        # Try to find a match
        match = process.extractOne(token, known_terms, scorer=fuzz.ratio)
        if match:
            best_match, score, _ = match
            # High threshold for spelling correction to avoid false positives
            if score >= 80: 
                normalized_tokens.append(best_match)
            else:
                normalized_tokens.append(token)
        else:
            normalized_tokens.append(token)
            
    return " ".join(normalized_tokens)
