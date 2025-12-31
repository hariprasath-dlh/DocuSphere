def synthesize_answer(chunks, max_length=800):
    """
    Create a clean, readable answer from retrieved chunks
    """
    seen = set()
    sentences = []

    for chunk in chunks:
        chunk = chunk.replace("\n", " ").strip()
        if chunk and chunk not in seen:
            seen.add(chunk)
            sentences.append(chunk)

    answer = " ".join(sentences)

    # Limit answer length (important!)
    if len(answer) > max_length:
        answer = answer[:max_length] + "..."

    return answer
