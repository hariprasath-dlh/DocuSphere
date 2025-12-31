def decompose_query(query: str):
    """
    Break a complex query into sub-questions.
    Rule-based version (offline, simple).
    """

    query = query.strip()

    # Common separators that indicate multiple intents
    separators = [" and ", ",", " also ", " & "]

    sub_queries = [query]

    for sep in separators:
        temp = []
        for q in sub_queries:
            if sep in q.lower():
                parts = q.split(sep)
                temp.extend([p.strip() for p in parts if p.strip()])
            else:
                temp.append(q)
        sub_queries = temp

    # Ensure each sub-query looks like a question
    final_queries = []
    for q in sub_queries:
        if not q.endswith("?"):
            q = q + "?"
        final_queries.append(q)

    return final_queries
