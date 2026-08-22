import argparse
import os
import sys
from typing import Any, Sequence

from llm_sdk import Small_LLM_Model
from src.agentics.prompts import handle_prompt
from src.errors.types import CallMeMaybeError
from src.imports.safe_imports import configure_local_download_cache
from src.parsing.parser import dump_json, get_data_from_input, load_to_json


def call_me_maybe(
    input: str = "data/input/function_calling_tests.json",
    output: str = "data/output/function_calling_results.json",
    fns: str = "data/input/functions_definition.json",
) -> Any:
    """Run the function-calling pipeline over all prompts in the input file."""
    configure_local_download_cache()
    data = get_data_from_input(input, fns)
    llm = Small_LLM_Model()

    i = 0
    results = "["
    print("[", end="", flush=True)
    for prompt_idx, prompt in enumerate(data["input"]):
        try:
            result = handle_prompt(
                llm, dump_json(prompt["prompt"]), data["functions"]
            )
            print(result, end="", flush=True)
            results += result
        except CallMeMaybeError as exc:
            error_msg = f'{{"error": "{exc.__class__.__name__}: {exc}"}}'
            print(error_msg, end="", flush=True)
            results += error_msg
        except Exception as exc:
            error_msg = f'{{"error": "Unexpected error: {exc}"}}'
            print(error_msg, end="", flush=True)
            results += error_msg

        if i < len(data["input"]) - 1:
            results += ",\n"
            print(",\n", end="", flush=True)
            i += 1

    results += "]"
    print("]", end="", flush=True)

    results = load_to_json(results)

    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output, "w") as output_file:
        output_file.write(dump_json(results))

    return results


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI arguments and run the project entrypoint."""
    parser = argparse.ArgumentParser(
        description="Run the function-calling pipeline."
    )
    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json",
        help="Path to the JSON file defining the callable functions.",
    )
    parser.add_argument(
        "--input",
        default="data/input/function_calling_tests.json",
        help="Path to the prompt input JSON file.",
    )
    parser.add_argument(
        "--output",
        default="data/output/function_calling_results.json",
        help="Path where the output should be written.",
    )
    args = parser.parse_args(argv)

    try:
        call_me_maybe(
            input=args.input, output=args.output, fns=args.functions_definition
        )
        return 0
    except CallMeMaybeError as exc:
        print(f"Error: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
