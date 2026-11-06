"""pytest config and shared fixtures"""

import pytest

from src.models import (
    FunctionCall,
    FunctionCallResult,
    FunctionDefinition,
    ParameterDefinition,
    PromptInput,
    ReturnDefinition,
)


@pytest.fixture
def sample_number_param():
    "fixture for a number parameter"
    return ParameterDefinition(
        type="number", description="A numeric parameter"
    )


@pytest.fixture
def sample_string_param():
    "fixture for a string parameter"
    return ParameterDefinition(type="string", description="A string parameter")


@pytest.fixture
def sample_add_function():
    "fixture for an add function definition"
    return FunctionDefinition(
        name="fn_add",
        description="Add two numbers together",
        parameters={
            "a": ParameterDefinition(type="number"),
            "b": ParameterDefinition(type="number"),
        },
        returns=ReturnDefinition(type="number"),
    )


@pytest.fixture
def sample_greet_function():
    "fixture for a greet function definition"
    return FunctionDefinition(
        name="fn_greet",
        description="Generate a greeting message",
        parameters={
            "name": ParameterDefinition(type="string"),
        },
        returns=ReturnDefinition(type="string"),
    )


@pytest.fixture
def sample_functions():
    "provide several function definitions for tests"
    return [
        FunctionDefinition(
            name="fn_add",
            description="Add two numbers",
            parameters={
                "a": ParameterDefinition(type="number"),
                "b": ParameterDefinition(type="number"),
            },
        ),
        FunctionDefinition(
            name="fn_greet",
            description="Greet someone",
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


@pytest.fixture
def sample_prompt():
    "fixture for a prompt input"
    return PromptInput(prompt="What is the sum of 2 and 3?")


@pytest.fixture
def sample_function_call():
    "fixture for a function call"
    return FunctionCall(name="fn_add", parameters={"a": 2, "b": 3})


@pytest.fixture
def sample_function_call_result():
    "fixture for a successful function call result"
    return FunctionCallResult(
        name="fn_add", parameters={"a": 2, "b": 3}, result=5
    )


@pytest.fixture
def sample_error_result():
    "fixture for an error function call result"
    return FunctionCallResult(
        name="fn_divide", parameters={"a": 1, "b": 0}, error="Division by zero"
    )
