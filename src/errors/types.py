"""Custom exception hierarchy for the function-calling pipeline."""


class CallMeMaybeError(Exception):
    """Base exception for all project-specific errors."""

    pass


class FileToJSONError(CallMeMaybeError):
    """Error reading or parsing JSON from file."""

    pass


class SchemaValidationError(CallMeMaybeError):
    """Error validating function schema or parameter definitions."""

    pass


class FunctionNotFoundError(CallMeMaybeError):
    """Error when selected function name does not exist in definitions."""

    pass


class ParameterGenerationError(CallMeMaybeError):
    """Error during parameter value generation from model."""

    pass


class ParameterTimeoutError(ParameterGenerationError):
    """Error when parameter generation exceeds maximum steps."""

    pass


class ParameterTypeError(ParameterGenerationError):
    """Error when generated parameter value does not match expected type."""

    pass


class OutputValidationError(CallMeMaybeError):
    """Error validating generated output against schema."""

    pass


class FunctionSelectionError(CallMeMaybeError):
    """Error during function name selection from model."""

    pass
