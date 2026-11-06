import argparse
import json
import os
import sys
from typing import Any, Sequence

from llm_sdk import Small_LLM_Model
from src.agentics.prompts import handle_prompt
from src.errors.types import (
    CallMeMaybeError,
    ModelLoadError,
    OutputWriteError,
    PipelineOutputError,
)
from src.parsing.parser import dump_json, get_data_from_input, load_to_json


def _load_llm() -> Any:
    "load the local llm, wrapping any failure in a project-specific error"
    try:
        return Small_LLM_Model()
    except Exception as exc:
        raise ModelLoadError(f"Failed to load the LLM model: {exc}")


def call_me_maybe(
    input: str = "data/input/function_calling_tests.json",
    output: str = "data/output/function_calling_results.json",
    fns: str = "data/input/functions_definition.json",
) -> Any:
    "run the function-calling pipeline over all prompts in the input file"
    data = get_data_from_input(input, fns)
    llm = _load_llm()

    prompts = data["input"]
    last_index = len(prompts) - 1
    results = "["
    print("[", end="", flush=True)

    for index, prompt in enumerate(prompts):
        try:
            result = handle_prompt(
                llm, dump_json(prompt["prompt"]), data["functions"]
            )
            print(result, end="", flush=True)
            results += result
        except CallMeMaybeError as exc:
            error_msg = json.dumps(
                {"error": f"{exc.__class__.__name__}: {exc}"}
            )
            print(error_msg, end="", flush=True)
            results += error_msg
        except Exception as exc:
            error_msg = json.dumps({"error": f"Unexpected error: {exc}"})
            print(error_msg, end="", flush=True)
            results += error_msg

        if index < last_index:
            results += ",\n"
            print(",\n", end="", flush=True)

    results += "]"
    print("]", end="", flush=True)

    try:
        parsed_results = load_to_json(results)
    except Exception as exc:
        raise PipelineOutputError(
            f"Failed to parse combined pipeline output as JSON: {exc}"
        )

    output_dir = os.path.dirname(output)
    try:
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(output, "w") as output_file:
            output_file.write(dump_json(parsed_results))
    except OSError as exc:
        raise OutputWriteError(f"Failed to write output to {output}: {exc}")

    return parsed_results


def main(argv: Sequence[str] | None = None) -> int:
    "parse cli args and run the project entrypoint"
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
