import json
from typing import Any, Dict, List

from pydantic import ValidationError

from src.errors.types import FileToJSONError, SchemaValidationError
from src.models import FunctionDefinition, PromptInput


def _validate_functions_schema(functions: Any) -> List[Dict[str, Any]]:
    "validate functions with the function definition model"
    if not isinstance(functions, list):
        raise SchemaValidationError(
            f"Functions must be a list, got {type(functions).__name__}."
        )

    validated: List[Dict[str, Any]] = []
    for i, func in enumerate(functions):
        try:
            model = FunctionDefinition.model_validate(func)
        except ValidationError as exc:
            raise SchemaValidationError(
                f"Function at index {i} is invalid: {exc}"
            )
        validated.append(model.model_dump())

    return validated


def _validate_prompts_schema(prompts: Any) -> List[Dict[str, Any]]:
    "validate input prompts with the prompt input model"
    if not isinstance(prompts, list):
        raise SchemaValidationError(
            f"Input prompts must be a list, got {type(prompts).__name__}."
        )

    validated: List[Dict[str, Any]] = []
    for i, item in enumerate(prompts):
        try:
            model = PromptInput.model_validate(item)
        except ValidationError as exc:
            raise SchemaValidationError(
                f"Prompt at index {i} is invalid: {exc}"
            )
        validated.append(model.model_dump())

    return validated


def get_data_from_input(input: str, functions: str) -> Dict[str, Any]:
    "read input and function definitions from json files and check the schema"
    decoder = json.decoder.JSONDecoder()
    try:
        with open(input) as input_file:
            input_data = decoder.decode(s=input_file.read())
    except FileNotFoundError:
        raise FileToJSONError(f"Input file not found: {input}")
    except json.JSONDecodeError as e:
        raise FileToJSONError(f"Invalid JSON in {input}: {e}")
    except Exception as e:
        raise FileToJSONError(f"Error reading/parsing from {input}: {e}")

    try:
        with open(functions) as functions_file:
            function_data = decoder.decode(s=functions_file.read())
    except FileNotFoundError:
        raise FileToJSONError(f"Functions file not found: {functions}")
    except json.JSONDecodeError as e:
        raise FileToJSONError(f"Invalid JSON in {functions}: {e}")
    except Exception as e:
        raise FileToJSONError(f"Error reading/parsing from {functions}: {e}")

    validated_functions = _validate_functions_schema(function_data)
    validated_prompts = _validate_prompts_schema(input_data)

    return {"input": validated_prompts, "functions": validated_functions}


def load_to_json(json_str: str) -> Any:
    "load a json string into python data"
    return json.loads(json_str)


# this keeps json strings safe when model output is missing escapes
# this can break json.loads

def dump_json(string: str) -> str:
    "turn a string into a json string for safe output"
    return json.dumps(string, indent=2)
