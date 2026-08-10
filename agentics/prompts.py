from typing import Any
import json
from .trie import build_trie, allowed_next_tokens, constrained_next_token


BLACKLIST = ',{}"[]()\t\n'
REGEX_BLACKLIST = '",'


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
        f"'boolean' must be written according to Python: 'True' or 'False'\n"
        f"'number' must be written according to Python's float type\n"
        f"'integer' must be written according to Python's int type\n"
        f"If the type is 'string' it could be anything "
        f"from a name to a REGEX or SQL (in the correct text format)."
        f"In the case of a string do not include single or double quotes"
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


def handle_params(functions: Any,
                  llm: Any,
                  input: str,
                  fn_name: str) -> str:
    selected_function = None
    for function in functions:
        if function["name"] == fn_name:
            selected_function = function
            break

    if selected_function is None:
        raise ValueError(f"Unknown function: {fn_name}")

    output = '{'

    params = selected_function["parameters"]

    for i, (param_name, param_info) in enumerate(params.items()):
        output += f'"{param_name}": '

        param_type = param_info["type"]
        if param_name == "regex":
            blacklist = REGEX_BLACKLIST
        else:
            blacklist = BLACKLIST
        if param_type == "string":
            output += '"'

        llm_output = ""

        tokens = llm.encode(input + output).tolist()[0]

        while True:
            logits = llm.get_logits_from_input_ids(tokens)

            next_token = max(range(len(logits)), key=logits.__getitem__)

            text = llm.decode([next_token])

            if any(c in blacklist for c in text):
                llm_output += text.strip(blacklist)

                if param_type == "number":
                    value = float(llm_output)

                    output += str(value)

                elif param_type == "integer":
                    value = int(llm_output)

                    output += str(value)

                elif param_type == "boolean":
                    value = bool(llm_output)

                    output += str(value)

                elif param_type == "string":
                    output += llm_output + '"'

                if i < len(params) - 1:
                    output += ", "
                break

            else:
                tokens.append(next_token)
                llm_output += text

    return output


def handle_prompt(llm: Any, prompt: str, functions: str) -> str:
    input = promptify(prompt, functions)

    input = input + '{\n\t"prompt": ' + prompt + ',\n\t"name": "'
    output = '{\n\t"prompt": ' + prompt + ',\n\t"name": "'

    fn_name = handle_name(functions, llm, input)
    input += fn_name + '",\n\t"parameters":'
    output += fn_name + '",\n\t"parameters":'

    fn_params = handle_params(functions, llm, input, fn_name)
    input += fn_params + '}\n}'
    output += fn_params + '}\n}'

    return output
