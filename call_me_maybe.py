import json
# from typing import Any
from parsing.parser import get_data_from_input
from imports.safe_imports import configure_local_download_cache, get_llm


def call_me_maybe(input: str = "data/input/function_calling_tests.json",
                  output: str = "data/input/function_calls.json",
                  fns: str = "data/input/functions_definition.json") -> str:
    configure_local_download_cache()
    print(json.dumps(get_data_from_input(input, fns), indent=2))
    llm = get_llm()()

    return ""


if __name__ == "__main__":
    try:
        print(call_me_maybe())
    except Exception as e:
        print(f"Error: {e}")
