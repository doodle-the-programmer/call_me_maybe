"""custom exception hierarchy for the function-calling pipeline"""


class CallMeMaybeError(Exception):
    "base class for all project-specific errors"

    pass


class FileToJSONError(CallMeMaybeError):
    "error reading or parsing json from a file"

    pass


class SchemaValidationError(CallMeMaybeError):
    "error validating function schema or parameter definitions"

    pass


class FunctionNotFoundError(CallMeMaybeError):
    "error when the selected function name is not in the definitions"

    pass


class ParameterGenerationError(CallMeMaybeError):
    "error during parameter value generation from the model"

    pass


class ParameterTimeoutError(ParameterGenerationError):
    "error when parameter generation runs past the step limit"

    pass


class ParameterTypeError(ParameterGenerationError):
    "error when a generated parameter value does not match the expected type"

    pass


class OutputValidationError(CallMeMaybeError):
    "error validating generated output against the schema"

    pass


class FunctionSelectionError(CallMeMaybeError):
    "error during function name selection from the model"

    pass


class CacheConfigurationError(CallMeMaybeError):
    "error setting up local model download cache directories"

    pass


class ModelLoadError(CallMeMaybeError):
    "error loading the llm used to run the pipeline"

    pass


class OutputWriteError(CallMeMaybeError):
    "error writing pipeline results to the output file"

    pass


class PipelineOutputError(CallMeMaybeError):
    "error parsing the combined pipeline results as json"

    pass
