"""tests for the pydantic models"""

import json

import pytest
from pydantic import ValidationError

from src.models import (
    FunctionCall,
    FunctionCallResult,
    FunctionDefinition,
    ParameterDefinition,
    PromptInput,
)


def make_function(**overrides):
    "build a valid function definition, overriding any field"
    data = {
        "name": "fn_add",
        "description": "Add two numbers",
        "parameters": {"a": {"type": "number"}, "b": {"type": "number"}},
    }
    return FunctionDefinition(**{**data, **overrides})


@pytest.mark.parametrize(
    "param_type", ["string", "number", "integer", "boolean"]
)
def test_parameter_accepts_valid_types(param_type):
    assert ParameterDefinition(type=param_type).type == param_type


@pytest.mark.parametrize("param_type", ["invalid", ""])
def test_parameter_rejects_invalid_types(param_type):
    with pytest.raises(ValidationError, match="type must be one of"):
        ParameterDefinition(type=param_type)


def test_function_definition_valid():
    fn = make_function(returns={"type": "number"})
    assert fn.name == "fn_add"
    assert len(fn.parameters) == 2
    # nested dicts are converted into ParameterDefinition models
    assert isinstance(fn.parameters["a"], ParameterDefinition)
    assert fn.returns.type == "number"


def test_function_definition_returns_is_optional():
    assert make_function().returns is None


@pytest.mark.parametrize("name", ["", "123-invalid", "has space"])
def test_function_definition_rejects_bad_name(name):
    with pytest.raises(ValidationError):
        make_function(name=name)


def test_function_definition_rejects_empty_parameters():
    with pytest.raises(ValidationError, match="parameters cannot be empty"):
        make_function(parameters={})


@pytest.mark.parametrize("prompt", ["", "   \n\t  "])
def test_prompt_rejects_blank(prompt):
    with pytest.raises(ValidationError):
        PromptInput(prompt=prompt)


@pytest.mark.parametrize("name", ["", "   "])
def test_function_call_and_result_reject_blank_name(name):
    with pytest.raises(ValidationError):
        FunctionCall(name=name, parameters={})
    with pytest.raises(ValidationError):
        FunctionCallResult(name=name, parameters={})


def test_function_call_accepts_empty_and_mixed_parameters():
    assert FunctionCall(name="fn", parameters={}).parameters == {}
    params = {"s": "hi", "f": 3.14, "i": 1, "b": True, "l": [1, 2]}
    assert FunctionCall(name="fn", parameters=params).parameters == params


def test_function_call_rejects_non_dict_parameters():
    with pytest.raises(ValidationError):
        FunctionCall(name="fn", parameters="not a dict")


def test_function_call_result_success_and_error():
    ok = FunctionCallResult(name="fn_add", parameters={"a": 1}, result=5)
    assert ok.result == 5
    assert ok.error is None

    failed = FunctionCallResult(
        name="fn_div", parameters={"a": 1}, error="Division by zero"
    )
    assert failed.result is None
    assert failed.error == "Division by zero"


@pytest.mark.parametrize(
    "model",
    [
        make_function(returns={"type": "number"}),
        PromptInput(prompt="What is 2 + 3?"),
        FunctionCall(name="fn_add", parameters={"a": 2, "b": 3}),
        FunctionCallResult(name="fn_add", parameters={"a": 2}, result=5),
    ],
)
def test_json_roundtrip(model):
    restored = type(model).model_validate_json(model.model_dump_json())
    assert restored == model


@pytest.mark.parametrize(
    "path, model",
    [
        ("data/input/functions_definition.json", FunctionDefinition),
        ("data/input/function_calling_tests.json", PromptInput),
    ],
)
def test_project_data_files_are_valid(path, model):
    with open(path) as f:
        items = json.load(f)
    assert items
    for item in items:
        model.model_validate(item)
