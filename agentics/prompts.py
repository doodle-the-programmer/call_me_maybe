from imports.safe_imports import get_llm
from typing import Any
import json


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


def handle_prompt(llm: any, prompt: str, functions: str) -> str:
    output = promptify(prompt, functions)
    tokens = llm.encode()


def main() -> None:
    pass
    llm = get_llm()()

    prompt = promptify("What is 6 times 7?")
    tokens = llm.encode(prompt).tolist()[0]

    MAX_NEW_TOKENS = 1000
    SOS_TOKEN_ID = llm._tokenizer.convert_tokens_to_ids("<|im_start|>") # dont use this in the final project
    EOS_TOKEN_ID = llm._tokenizer.convert_tokens_to_ids("<|im_end|>") # dont use this in final project
    THINK_START = llm._tokenizer.convert_tokens_to_ids("<think>")
    THINK_END = llm._tokenizer.convert_tokens_to_ids("</think>")

    temperature = 0.8
    K = 50

    for _ in range(MAX_NEW_TOKENS):
        logits = llm.get_logits_from_input_ids(tokens)

        # 1. restrict to top-k
        top_k = sorted(range(len(logits)),
                       key=lambda i: logits[i],
                       reverse=True)[:K]

        # 2. softmax over top-k only
        sub_logits = [logits[i] / temperature for i in top_k]

        m = max(sub_logits)
        probs = [math.exp(l - m) for l in sub_logits]
        s = sum(probs)
        probs = [p / s for p in probs]

        # 3. sample
        next_token = random.choices(top_k, weights=probs, k=1)[0]

        if next_token == EOS_TOKEN_ID:
            break

        print(llm.decode([next_token]), end="", flush=True)
        tokens.append(next_token)

    print("\nCompleted!")

    # print(llm.decode(tokens))
