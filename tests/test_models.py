"""tests for pydantic models"""

import pytest
from pydantic import ValidationError

from src.models import (
    FunctionCall,
    FunctionCallResult,
    FunctionDefinition,
    ParameterDefinition,
    PromptInput,
    ReturnDefinition,
)


class TestParameterDefinition:
    "tests for the parameter definition model"

    def test_valid_parameter_definition(self):
        "test creating a valid parameter definition"
        param = ParameterDefinition(type="string")
        assert param.type == "string"
        assert param.description is None

    def test_parameter_with_description(self):
        "test a parameter definition with a description"
        param = ParameterDefinition(
            type="number", description="A numeric parameter"
        )
        assert param.type == "number"
        assert param.description == "A numeric parameter"

    def test_all_valid_types(self):
        "test all valid parameter types"
        for valid_type in ["string", "number", "integer", "boolean"]:
            param = ParameterDefinition(type=valid_type)
            assert param.type == valid_type

    def test_invalid_type_raises_error(self):
        "test that an invalid type raises validation error"
        with pytest.raises(ValidationError) as exc_info:
            ParameterDefinition(type="invalid")
        assert "type must be one of" in str(exc_info.value)

    def test_empty_type_raises_error(self):
        "test that an empty type raises validation error"
        with pytest.raises(ValidationError):
            ParameterDefinition(type="")


class TestReturnDefinition:
    "tests for the return definition model"

    def test_valid_return_definition(self):
        "test creating a valid return definition"
        ret = ReturnDefinition(type="string")
        assert ret.type == "string"
        assert ret.description is None

    def test_return_with_description(self):
        "test a return definition with a description"
        ret = ReturnDefinition(
            type="number", description="Returns a numeric value"
        )
        assert ret.type == "number"
        assert ret.description == "Returns a numeric value"


class TestFunctionDefinition:
    "tests for the function definition model"

    def test_valid_function_definition(self):
        "test creating a valid function definition"
        fn = FunctionDefinition(
            name="fn_add",
            description="Add two numbers",
            parameters={
                "a": ParameterDefinition(type="number"),
                "b": ParameterDefinition(type="number"),
            },
            returns=ReturnDefinition(type="number"),
        )
        assert fn.name == "fn_add"
        assert fn.description == "Add two numbers"
        assert len(fn.parameters) == 2
        assert fn.returns is not None

    def test_function_without_returns(self):
        "test a function definition without a return type"
        fn = FunctionDefinition(
            name="fn_print",
            description="Print something",
            parameters={
                "message": ParameterDefinition(type="string"),
            },
        )
        assert fn.returns is None

    def test_function_with_dict_parameters(self):
        "test a function definition that uses dict-style parameters"
        fn = FunctionDefinition(
            name="fn_test",
            description="Test function",
            parameters={
                "param1": {"type": "string"},
                "param2": {"type": "number"},
            },
        )
        assert len(fn.parameters) == 2
        assert isinstance(fn.parameters["param1"], ParameterDefinition)

    def test_invalid_function_name_raises_error(self):
        "test that an invalid function name raises validation error"
        with pytest.raises(ValidationError):
            FunctionDefinition(
                name="123-invalid",
                description="Bad name",
                parameters={
                    "a": ParameterDefinition(type="string"),
                },
            )

    def test_empty_function_name_raises_error(self):
        "test that an empty function name raises validation error"
        with pytest.raises(ValidationError):
            FunctionDefinition(
                name="",
                description="Empty name",
                parameters={
                    "a": ParameterDefinition(type="string"),
                },
            )

    def test_empty_parameters_raises_error(self):
        "test that an empty parameters dict raises validation error"
        with pytest.raises(ValidationError):
            FunctionDefinition(
                name="fn_test",
                description="No params",
                parameters={},
            )

    def test_function_definition_dict_conversion(self):
        "test converting a function definition to a dict"
        fn = FunctionDefinition(
            name="fn_add",
            description="Add two numbers",
            parameters={
                "a": ParameterDefinition(type="number"),
                "b": ParameterDefinition(type="number"),
            },
        )
        fn_dict = fn.model_dump()
        assert fn_dict["name"] == "fn_add"
        assert "parameters" in fn_dict
        assert len(fn_dict["parameters"]) == 2

    def test_function_definition_json_roundtrip(self):
        "test json serialization and deserialization"
        fn = FunctionDefinition(
            name="fn_greet",
            description="Greet someone",
            parameters={
                "name": ParameterDefinition(
                    type="string", description="Person's name"
                ),
            },
        )
        json_str = fn.model_dump_json()
        fn_restored = FunctionDefinition.model_validate_json(json_str)
        assert fn_restored.name == fn.name
        assert fn_restored.description == fn.description


class TestPromptInput:
    "tests for the prompt input model"

    def test_valid_prompt_input(self):
        "test creating a valid prompt input"
        prompt = PromptInput(prompt="What is the sum of 2 and 3?")
        assert prompt.prompt == "What is the sum of 2 and 3?"

    def test_empty_prompt_raises_error(self):
        "test that an empty prompt raises validation error"
        with pytest.raises(ValidationError):
            PromptInput(prompt="")

    def test_whitespace_only_prompt_raises_error(self):
        "test that whitespace-only input raises validation error"
        with pytest.raises(ValidationError):
            PromptInput(prompt="   \n\t  ")

    def test_prompt_input_json_roundtrip(self):
        "test json serialization and deserialization"
        prompt = PromptInput(prompt="Test prompt")
        json_str = prompt.model_dump_json()
        prompt_restored = PromptInput.model_validate_json(json_str)
        assert prompt_restored.prompt == prompt.prompt


class TestFunctionCall:
    "tests for the function call model"

    def test_valid_function_call(self):
        "test creating a valid function call"
        call = FunctionCall(name="fn_add", parameters={"a": 2, "b": 3})
        assert call.name == "fn_add"
        assert call.parameters == {"a": 2, "b": 3}

    def test_function_call_with_empty_parameters(self):
        "test a function call with an empty parameters dict"
        call = FunctionCall(name="fn_test", parameters={})
        assert call.name == "fn_test"
        assert call.parameters == {}

    def test_function_call_with_various_types(self):
        "test a function call with several parameter types"
        call = FunctionCall(
            name="fn_complex",
            parameters={
                "string_param": "hello",
                "number_param": 3.14,
                "int_param": 42,
                "bool_param": True,
                "list_param": [1, 2, 3],
            },
        )
        assert len(call.parameters) == 5

    def test_empty_function_name_raises_error(self):
        "test that an empty function name raises validation error"
        with pytest.raises(ValidationError):
            FunctionCall(name="", parameters={"a": 1})

    def test_whitespace_function_name_raises_error(self):
        "test that a whitespace-only function name raises validation error"
        with pytest.raises(ValidationError):
            FunctionCall(name="   ", parameters={"a": 1})

    def test_non_dict_parameters_raises_error(self):
        "test that a non-dict value raises validation error"
        with pytest.raises(ValidationError):
            FunctionCall(name="fn_test", parameters="not a dict")

    def test_function_call_json_roundtrip(self):
        "test json serialization and deserialization"
        call = FunctionCall(name="fn_add", parameters={"a": 5, "b": 10})
        json_str = call.model_dump_json()
        call_restored = FunctionCall.model_validate_json(json_str)
        assert call_restored.name == call.name
        assert call_restored.parameters == call.parameters


class TestFunctionCallResult:
    "tests for the function call result model"

    def test_successful_result(self):
        "test creating a successful function call result"
        result = FunctionCallResult(
            name="fn_add", parameters={"a": 2, "b": 3}, result=5
        )
        assert result.name == "fn_add"
        assert result.parameters == {"a": 2, "b": 3}
        assert result.result == 5
        assert result.error is None

    def test_error_result(self):
        "test creating a result with an error"
        result = FunctionCallResult(
            name="fn_divide",
            parameters={"a": 1, "b": 0},
            error="Division by zero",
        )
        assert result.name == "fn_divide"
        assert result.result is None
        assert result.error == "Division by zero"

    def test_result_with_complex_return(self):
        "test a result with a nested data structure"
        result = FunctionCallResult(
            name="fn_process",
            parameters={"data": [1, 2, 3]},
            result={"count": 3, "sum": 6, "average": 2},
        )
        assert isinstance(result.result, dict)
        assert result.result["sum"] == 6

    def test_result_with_none_result(self):
        "test a result with none as the result value"
        result = FunctionCallResult(name="fn_noop", parameters={}, result=None)
        assert result.result is None

    def test_empty_function_name_raises_error(self):
        "test that an empty function name raises validation error"
        with pytest.raises(ValidationError):
            FunctionCallResult(name="", parameters={}, result=None)

    def test_function_call_result_json_roundtrip(self):
        "test json serialization and deserialization"
        result = FunctionCallResult(
            name="fn_greet",
            parameters={"name": "Alice"},
            result="Hello, Alice!",
        )
        json_str = result.model_dump_json()
        result_restored = FunctionCallResult.model_validate_json(json_str)
        assert result_restored.name == result.name
        assert result_restored.parameters == result.parameters
        assert result_restored.result == result.result


class TestIntegration:
    "integration tests across several models"

    def test_build_full_pipeline(self):
        "test building a full pipeline from input to result"
        fn_def = FunctionDefinition(
            name="fn_add",
            description="Add two numbers",
            parameters={
                "a": ParameterDefinition(type="number"),
                "b": ParameterDefinition(type="number"),
            },
            returns=ReturnDefinition(type="number"),
        )
        prompt = PromptInput(prompt="What is 2 + 3?")
        call = FunctionCall(name="fn_add", parameters={"a": 2, "b": 3})
        result = FunctionCallResult(
            name="fn_add", parameters={"a": 2, "b": 3}, result=5
        )
        assert fn_def.name == call.name
        assert call.name == result.name
        assert prompt.prompt == "What is 2 + 3?"
        assert result.result == 5

    def test_multiple_functions(self):
        "test handling multiple function definitions"
        functions = [
            FunctionDefinition(
                name="fn_add",
                description="Add numbers",
                parameters={
                    "a": ParameterDefinition(type="number"),
                    "b": ParameterDefinition(type="number"),
                },
            ),
            FunctionDefinition(
                name="fn_greet",
                description="Greet a person",
                parameters={
                    "name": ParameterDefinition(type="string"),
                },
            ),
            FunctionDefinition(
                name="fn_reverse",
                description="Reverse a string",
                parameters={
                    "text": ParameterDefinition(type="string"),
                },
            ),
        ]

        assert len(functions) == 3
        assert all(fn.name for fn in functions)
        assert all(fn.parameters for fn in functions)
