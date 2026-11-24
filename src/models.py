"""pydantic models for the function-calling pipeline

Data flows through the models in this order:
    FunctionDefinition + PromptInput  (inputs read from the json files)
        -> FunctionCall               (what the llm generates)
        -> FunctionCallResult         (the call plus its result or error)

Each model validates its data when it is created, so invalid input
raises a pydantic ValidationError instead of failing later in the pipeline.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class ParameterDefinition(BaseModel):
    "schema for a function parameter"

    type: str = Field(
        ...,
        description="Type of the parameter "
        "(string, number, integer, boolean)",
    )
    description: Optional[str] = Field(
        None, description="Description of the parameter"
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        "check that the type is one of the allowed values"
        # only json-schema primitives are supported for parameters
        allowed_types = {"string", "number", "integer", "boolean"}
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}, got {v!r}")
        return v


class ReturnDefinition(BaseModel):
    "schema for a function return type"

    # unlike parameters, the return type is not restricted to a fixed set
    type: str = Field(..., description="Type of the return value")
    description: Optional[str] = Field(
        None, description="Description of the return value"
    )


class FunctionDefinition(BaseModel):
    "schema for a callable function"

    name: str = Field(..., description="Function name")
    description: str = Field(
        ..., description="Function description"
    )
    # maps each parameter name to its definition; plain dicts coming from
    # json are converted into ParameterDefinition automatically by pydantic
    parameters: Dict[str, ParameterDefinition] = Field(
        ..., description="Function parameters"
    )
    # optional because some functions return nothing
    returns: Optional[ReturnDefinition] = Field(
        None, description="Return type definition"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        "check that the function name follows the allowed pattern"
        # isidentifier() ensures a valid python name (no spaces, dashes or
        # leading digits), so the name can be used as a function name
        if not v:
            raise ValueError("name cannot be empty")
        if not v.isidentifier():
            raise ValueError(f"name {v!r} is not a valid identifier")
        return v

    @field_validator("parameters")
    @classmethod
    def validate_parameters(
        cls, v: Dict[str, ParameterDefinition]
    ) -> Dict[str, ParameterDefinition]:
        "check that parameters is not empty"
        # every function must take at least one argument for the llm to fill
        if not v:
            raise ValueError("parameters cannot be empty")
        return v


class PromptInput(BaseModel):
    "schema for a single prompt input"

    # natural language request, e.g. "What is the sum of 2 and 3?"
    prompt: str = Field(..., description="The user prompt")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        "check that the prompt is not empty"
        # strip() also rejects prompts made only of whitespace
        if not v or not v.strip():
            raise ValueError("prompt cannot be empty")
        return v


class FunctionCall(BaseModel):
    "schema for a generated function call"

    name: str = Field(..., description="Function name to call")
    # Any: the values are produced by the llm and can be str, int, float...
    parameters: Dict[str, Any] = Field(..., description="Function parameters")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        "check that the function name is not empty"
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        "check that parameters is a dict"
        # extra safety net: pydantic already rejects non-dict values
        if not isinstance(v, dict):
            raise ValueError(f"parameters must be a dict, got {type(v)}")
        return v


class FunctionCallResult(BaseModel):
    "schema for a function call result"

    name: str = Field(..., description="Function name called")
    parameters: Dict[str, Any] = Field(
        ..., description="Parameters passed to function"
    )
    # result and error are mutually exclusive in practice: a successful call
    # has a result and no error, a failed call has an error and no result
    result: Optional[Any] = Field(
        None, description="Result from function call"
    )
    error: Optional[str] = Field(
        None, description="Error message if call failed"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        "check that the function name is not empty"
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v
