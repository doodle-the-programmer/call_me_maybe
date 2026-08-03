from parsing.parser import get_data_from_input, load_to_json, dump_json
from imports.safe_imports import configure_local_download_cache, get_llm
from agentics.prompts import handle_prompt


def call_me_maybe(input: str = "data/input/function_calling_tests.json",
                  output: str = "data/input/function_calls.json",
                  fns: str = "data/input/functions_definition.json") -> any:
    configure_local_download_cache()
    data = get_data_from_input(input, fns)
    llm = get_llm()()

    i = 0
    results = '['
    print('[', end="", flush=True)
    for prompt in data["input"]:
        result = handle_prompt(llm,
                               dump_json(prompt["prompt"]),
                               data["functions"])
        print(result, end="", flush=True)
        results += result

        if i < len(data["input"]) - 1:
            results += ',\n'
            print(',\n', end="", flush=True)
            i += 1

    results += ']'
    print(']', end="", flush=True)

    return load_to_json(results)


if __name__ == "__main__":
    try:
        result = call_me_maybe()
        print(result)
        print(type(result))
    except Exception as e:
        print(f"Error: {e}")
