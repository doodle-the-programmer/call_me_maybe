def build_trie(function_names, llm):
    """Build a trie of tokenized function names for constrained decoding."""
    root = {"children": {}, "end": False}

    for name in function_names:
        tokens = llm.encode(name).tolist()[0]

        node = root
        for t in tokens:
            if t not in node["children"]:
                node["children"][t] = {"children": {}, "end": False}
            node = node["children"][t]

        node["end"] = True

    return root


def allowed_next_tokens(trie_root, token_seq):
    """Get valid token continuations from current position in trie."""
    node = trie_root

    for t in token_seq:
        if t not in node["children"]:
            return set()
        node = node["children"][t]

    return set(int(x) for x in node["children"].keys())


def constrained_next_token(logits, allowed_tokens):
    """Select highest-scoring token from allowed set of tokens."""
    allowed = list(allowed_tokens)
    if not allowed:
        raise ValueError("allowed_tokens cannot be empty")

    # For larger candidate sets, use native vectorized argmax if available.
    if len(allowed) >= 32 and hasattr(logits, "argmax"):
        subset = logits[allowed]
        best_pos = int(subset.argmax())
        return int(allowed[best_pos])

    # Small candidate sets are often faster with a tight Python loop.
    best = allowed[0]
    best_val = logits[best]
    for tok in allowed[1:]:
        val = logits[tok]
        if val > best_val:
            best = tok
            best_val = val
    return int(best)
