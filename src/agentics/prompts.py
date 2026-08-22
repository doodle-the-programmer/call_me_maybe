import json
from typing import Any

from src.errors.types import (
    FunctionNotFoundError,
    FunctionSelectionError,
    ParameterGenerationError,
    ParameterTypeError,
)

from .trie import allowed_next_tokens, build_trie, constrained_next_token

BLACKLIST = ',{}"[]()\t\n'
REGEX_BLACKLIST = '",'


def is_end(trie, token_seq):
    """Check if token sequence is a valid end point in the trie."""
    node = trie
    for t in token_seq:
        node = node["children"][t]
    return node["end"]


def promptify(user_text: str, functions: Any) -> str:
    """Build system prompt with function definitions and user text."""
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
    """Select function name using trie-constrained token generation."""
    try:
        output = ""
        function_names = [f["name"] for f in functions]
        if not function_names:
            raise FunctionSelectionError("No functions available to select.")

        trie = build_trie(function_names, llm)
        tokens = llm.encode(input).tolist()[0]
        name_tokens = []

        for step in range(64):
            logits = llm.get_logits_from_input_ids(tokens)
            allowed = allowed_next_tokens(trie, name_tokens)

            if not allowed:
                break

            current = constrained_next_token(logits, allowed)
            tokens.append(current)
            name_tokens.append(current)

            decode = llm.decode([current])
            output += decode

            if is_end(trie, name_tokens):
                break
        else:
            raise FunctionSelectionError(
                f"Function name selection exceeded 64 steps. "
                f"Selected: {output!r}"
            )

        if not output or output not in function_names:
            raise FunctionSelectionError(
                f"Invalid function name selected: {output!r}"
            )

        return output
    except FunctionSelectionError:
        raise
    except Exception as exc:
        raise FunctionSelectionError(
            f"Error during function name selection: {exc}"
        )


def _validate_param_value(
    value: str, param_type: str, param_name: str
) -> None:
    """Validate that a generated value matches its parameter type."""
    try:
        if param_type == "boolean" and value not in {"True", "False"}:
            raise ParameterTypeError(
                f"Parameter {param_name!r}: boolean value {value!r} "
                f"is not 'True' or 'False'."
            )
        if param_type == "integer":
            int(value)
        if param_type == "number":
            float(value)
        if param_type == "string" and not value:
            raise ParameterTypeError(
                f"Parameter {param_name!r}: string value cannot be empty."
            )
    except (ValueError, TypeError) as exc:
        raise ParameterTypeError(
            f"Parameter {param_name!r}: expected {param_type}, "
            f"got {value!r}. {exc}"
        )


def handle_params(functions: Any, llm: Any, input: str, fn_name: str) -> str:
    """Generate JSON parameters using schema-aware token selection."""
    try:
        selected_function = None
        for function in functions:
            if function["name"] == fn_name:
                selected_function = function
                break

        if selected_function is None:
            raise FunctionNotFoundError(
                f"Function {fn_name!r} not found in definitions."
            )

        output = "{"
        params = selected_function["parameters"]

        for i, (param_name, param_info) in enumerate(params.items()):
            output += f'"{param_name}": '

            param_type = param_info.get("type")
            if not param_type:
                raise ParameterGenerationError(
                    f"Parameter {param_name!r} has no 'type' field in schema."
                )

            blacklist = REGEX_BLACKLIST if param_name == "regex" else BLACKLIST
            if param_type == "string":
                output += '"'

            llm_output = ""
            tokens = llm.encode(input + output).tolist()[0]

            for step in range(64):
                logits = llm.get_logits_from_input_ids(tokens)
                next_token = max(range(len(logits)), key=logits.__getitem__)
                text = llm.decode([next_token])

                if any(c in blacklist for c in text):
                    llm_output += text.strip(blacklist)
                    _validate_param_value(llm_output, param_type, param_name)

                    if param_type == "number":
                        value = float(llm_output)
                        output += str(value)
                    elif param_type == "integer":
                        value = int(llm_output)
                        output += str(value)
                    elif param_type == "boolean":
                        value = llm_output.strip().lower() == "true"
                        output += str(value)
                    elif param_type == "string":
                        output += llm_output + '"'
                    else:
                        output += llm_output

                    if i < len(params) - 1:
                        output += ", "
                    break
                else:
                    tokens.append(next_token)
                    llm_output += text
            else:
                raise ParameterGenerationError(
                    f"Parameter {param_name!r} ({param_type}) "
                    f"generation exceeded 64 steps. "
                    f"Partial value: {llm_output!r}"
                )

        output += "}"
        return output
    except (
        ParameterGenerationError,
        ParameterTypeError,
        FunctionNotFoundError,
    ):
        raise
    except Exception as exc:
        raise ParameterGenerationError(
            f"Error building parameters for {fn_name!r}: {exc}"
        )


def handle_prompt(llm: Any, prompt: str, functions: str) -> str:
    input = promptify(prompt, functions)

    input = input + '{\n\t"prompt": ' + prompt + ',\n\t"name": "'
    output = '{\n\t"prompt": ' + prompt + ',\n\t"name": "'

    fn_name = handle_name(functions, llm, input)
    input += fn_name + '",\n\t"parameters":'
    output += fn_name + '",\n\t"parameters":'

    fn_params = handle_params(functions, llm, input, fn_name)
    input += fn_params + "\n}"
    output += fn_params + "\n}"

    return output
