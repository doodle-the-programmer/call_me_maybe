"""Tests for pydantic models with real project data."""

import json

from src.models import (
    FunctionCall,
    FunctionCallResult,
    FunctionDefinition,
    PromptInput,
)


class TestRealDataValidation:
    """Tests using real data from the project files."""

    def test_load_function_definitions_from_json(self):
        """Test loading and validating function definitions from JSON."""
        with open("data/input/functions_definition.json") as f:
            functions_data = json.load(f)
        functions = [
            FunctionDefinition.model_validate(fn) for fn in functions_data
        ]

        assert len(functions) > 0
        assert all(fn.name for fn in functions)
        assert all(fn.description for fn in functions)
        assert all(fn.parameters for fn in functions)

    def test_load_prompts_from_json(self):
        """Test loading and validating prompts from JSON."""
        with open("data/input/function_calling_tests.json") as f:
            prompts_data = json.load(f)
        prompts = [
            PromptInput.model_validate(prompt) for prompt in prompts_data
        ]

        assert len(prompts) > 0
        assert all(prompt.prompt for prompt in prompts)

    def test_generated_function_calls_validation(self):
        """Test validating generated function call outputs."""
        calls = [
            FunctionCall(
                name="fn_add_numbers", parameters={"a": 2.0, "b": 3.0}
            ),
            FunctionCall(name="fn_greet", parameters={"name": "Alice"}),
            FunctionCall(name="fn_reverse_string", parameters={"s": "hello"}),
        ]
        for call in calls:
            assert call.name
            assert call.parameters

    def test_function_call_results_validation(self):
        """Test validating function call results."""
        results = [
            FunctionCallResult(
                name="fn_add_numbers",
                parameters={"a": 2.0, "b": 3.0},
                result=5.0,
            ),
            FunctionCallResult(
                name="fn_greet",
                parameters={"name": "Bob"},
                result="Hello, Bob!",
            ),
            FunctionCallResult(
                name="fn_error_case",
                parameters={"value": -1},
                error="Negative value not allowed",
            ),
        ]
        for result in results:
            assert result.name
            if result.error:
                assert result.result is None
            else:
                assert result.result is not None

    def test_round_trip_validation(self):
        """Test round-trip validation through JSON."""
        with open("data/input/functions_definition.json") as f:
            functions_data = json.load(f)
        for fn_data in functions_data[:3]:
            fn = FunctionDefinition.model_validate(fn_data)
            fn_dict = fn.model_dump()

            # Validate the dict can be re-parsed
            fn_restored = FunctionDefinition.model_validate(fn_dict)
            assert fn_restored.name == fn.name
            assert fn_restored.description == fn.description
