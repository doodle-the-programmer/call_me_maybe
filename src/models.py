"""Pydantic models for function calling pipeline."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class ParameterDefinition(BaseModel):
    """Schema for a function parameter."""

    type: str = Field(
        ...,
        description="Type of the parameter "
        "(string, number, integer, boolean)",
    )
    description: Optional[str] = Field(
        None, description="Human-readable description of the parameter"
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that type is one of the allowed values."""
        allowed_types = {"string", "number", "integer", "boolean"}
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}, got {v!r}")
        return v


class ReturnDefinition(BaseModel):
    """Schema for a function return type."""

    type: str = Field(..., description="Type of the return value")
    description: Optional[str] = Field(
        None, description="Description of the return value"
    )


class FunctionDefinition(BaseModel):
    """Schema for a callable function."""

    name: str = Field(..., description="Function name")
    description: str = Field(
        ..., description="Human-readable function description"
    )
    parameters: Dict[str, ParameterDefinition] = Field(
        ..., description="Function parameters"
    )
    returns: Optional[ReturnDefinition] = Field(
        None, description="Return type definition"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that function name follows a pattern."""
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
        """Validate that parameters is not empty."""
        if not v:
            raise ValueError("parameters cannot be empty")
        return v


class PromptInput(BaseModel):
    """Schema for a single prompt input."""

    prompt: str = Field(..., description="The user prompt")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate that prompt is not empty."""
        if not v or not v.strip():
            raise ValueError("prompt cannot be empty")
        return v


class FunctionCall(BaseModel):
    """Schema for a generated function call."""

    name: str = Field(..., description="Function name to call")
    parameters: Dict[str, Any] = Field(..., description="Function parameters")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that function name is not empty."""
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that parameters is a dict."""
        if not isinstance(v, dict):
            raise ValueError(f"parameters must be a dict, got {type(v)}")
        return v


class FunctionCallResult(BaseModel):
    """Schema for a function call result."""

    name: str = Field(..., description="Function name called")
    parameters: Dict[str, Any] = Field(
        ..., description="Parameters passed to function"
    )
    result: Optional[Any] = Field(
        None, description="Result from function call"
    )
    error: Optional[str] = Field(
        None, description="Error message if call failed"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that function name is not empty."""
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v
