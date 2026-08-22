import json
from typing import Any, Dict

from src.errors.types import FileToJSONError, SchemaValidationError


def _validate_functions_schema(functions: Any) -> None:
    """Validate that the functions schema is properly formatted."""
    if not isinstance(functions, list):
        raise SchemaValidationError(
            f"Functions must be a list, got {type(functions).__name__}."
        )
    for i, func in enumerate(functions):
        if not isinstance(func, dict):
            raise SchemaValidationError(
                f"Function at index {i} must be a dict, "
                f"got {type(func).__name__}."
            )
        if "name" not in func:
            raise SchemaValidationError(
                f"Function at index {i} is missing 'name' field."
            )
        if "parameters" not in func:
            raise SchemaValidationError(
                f"Function at index {i} is missing 'parameters' field."
            )
        params = func["parameters"]
        if not isinstance(params, dict):
            raise SchemaValidationError(
                f"Function {func['name']}: parameters must be a dict, "
                f"got {type(params).__name__}."
            )
        for param_name, param_info in params.items():
            if not isinstance(param_info, dict) or "type" not in param_info:
                raise SchemaValidationError(
                    f"Function {func['name']}, parameter {param_name!r}: "
                    f"missing or invalid 'type' field."
                )


def get_data_from_input(input: str, functions: str) -> Dict[str, Any]:
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

    _validate_functions_schema(function_data)

    return {"input": input_data, "functions": function_data}


def load_to_json(json_str: str) -> Any:
    return json.loads(json_str)


# This is here for a very particular case where when extracting the JSON data
# from calling_tests it doesnt add a \ before some of the "s,
# which later breaks json.loads
def dump_json(string: str) -> str:
    return json.dumps(string, indent=2)
