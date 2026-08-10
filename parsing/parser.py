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


def load_to_json(json_str: str) -> Any:
    return json.loads(json_str)


# This is here for a very particular case where when extracting the JSON data
# from calling_tests it doesnt add a \ before some of the "s,
# which later breaks json.loads
def dump_json(string: str) -> str:
    return json.dumps(string, indent=2)
