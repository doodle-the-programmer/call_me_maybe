from typing import Any
import json
from .trie import build_trie, allowed_next_tokens, constrained_next_token


def is_end(trie, token_seq):
    node = trie
    for t in token_seq:
        node = node["children"][t]
    return node["end"]



def promptify(user_text: str, functions: Any) -> str:
    return (
        f"<|im_start|>system\n"
        f"As an Agent you have access to the following functions:\n"
        f"{json.dumps(functions, indent=2)}\n"
        f"Output exactly one JSON object.\n"
        f"Do not include Markdown, explanations, or surrounding text:\n"
        """
        {
            "prompt": "What is the sum of 2 and 3?",
            "name": "fn_add_numbers",
            "parameters": {"a": 2.0, "b": 3.0}
        }
        """
        f"<|im_end|>\n"
        f"<|im_start|>user\n"
        f"{user_text}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def handle_name(functions: Any, llm: Any, input: str) -> str:
    output = ""
    names = ""

    function_names = [f["name"] for f in functions]
    trie = build_trie(function_names, llm)

    tokens = llm.encode(input).tolist()[0]

    name_tokens = []

    current = None

    while True:
        logits = llm.get_logits_from_input_ids(tokens)

        allowed = allowed_next_tokens(trie, name_tokens)

        if not allowed:
            break

        current = constrained_next_token(logits, allowed)

        tokens.append(current)
        name_tokens.append(current)

        decode = llm.decode([current])
        names += decode
        output += decode

        if is_end(trie, name_tokens):
            break

    return output


def handle_prompt(llm: Any, prompt: str, functions: str) -> str:
    output = promptify(prompt, functions)
    output = output + '{\n\t"prompt": "' + prompt + '",\n\t"name": "'
    print('{\n\t"prompt": "' + prompt + '",\n\t"name": "', end="", flush=True)

    fn_name = handle_name(functions, llm, output)
    output += fn_name + '",\n\t"parameters":'

    return output
