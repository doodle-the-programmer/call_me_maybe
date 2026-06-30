import json
from errors.types import FileToJSONError
from typing import Dict, Any


def get_data_from_input(input: str, functions: str) -> Dict[str, Any]:
    decoder = json.decoder.JSONDecoder()
    try:
        with open(input) as input_file:
            input_data = decoder.decode(s=input_file.read())
    except Exception as e:
        raise FileToJSONError(f"Error reading/parsing from {input}: {e}")
    try:
        with open(functions) as functions_file:
            function_data = decoder.decode(s=functions_file.read())
    except Exception as e:
        raise FileToJSONError(f"Error reading/parsing from {functions}: {e}")
    return {"input": input_data, "functions": function_data}
