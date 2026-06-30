def build_trie(function_names, llm):
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
    node = trie_root

    for t in token_seq:
        if t not in node["children"]:
            return set()  # invalid path (shouldn't happen)
        node = node["children"][t]

    return set(int(x) for x in node["children"].keys())


def constrained_next_token(logits, allowed_tokens):
    best = None
    best_val = float("-inf")

    for i in allowed_tokens:
        i = int(i)

        if logits[i] > best_val:
            best_val = logits[i]
            best = i

    return int(best)
