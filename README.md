*This project has been created as part of the 42 curriculum by gpatrici.*

# call_me_maybe

## Description

`call_me_maybe` is a function-calling pipeline powered by a small, locally
run language model. Given a natural language prompt (e.g. *"What is the
product of 3 and 5?"*) and a list of available function definitions (name,
description, parameters, return type), the program uses the LLM to:

1. Pick the correct function to call out of the available definitions.
2. Generate the parameters for that function call, respecting each
   parameter's declared type (string, number, integer, boolean).
3. Produce a structured JSON result describing the chosen function and its
   parameters.

The goal of the project is to explore **constrained decoding**: instead of
asking the model to freely generate text and hoping it produces valid JSON
with a valid function name, the program constrains, token by token, what the
model is allowed to output. This guarantees the function name always exists
in the provided definitions and that every parameter is syntactically valid
for its declared type, without needing a separate output-correction step.

The project is split into a small number of focused modules:

- [src/call_me_maybe.py](src/call_me_maybe.py): CLI entrypoint and the
  top-level pipeline loop
- [src/parsing/parser.py](src/parsing/parser.py): reading and validating the
  input/function JSON files
- [src/models.py](src/models.py): pydantic schemas used across the project
- [src/agentics/trie.py](src/agentics/trie.py): the token trie used for
  constrained function-name decoding
- [src/agentics/prompts.py](src/agentics/prompts.py): prompt building,
  function selection and parameter generation
- [src/errors/types.py](src/errors/types.py): the project's exception
  hierarchy
- [src/llm_sdk](src/llm_sdk): the local LLM wrapper used to load the model
  and run inference (provided as-is, not modified by this work)

## Instructions

### Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for dependency management
- enough disk space and memory to download and run a small local LLM
  (`Qwen/Qwen3-0.6B` by default)

### Installation

```sh
make install          # install runtime dependencies
make dev-install       # install runtime + dev dependencies (pytest, lint, etc)
```

This creates a project virtual environment (see `PROJECT_ENV` in the
[Makefile](Makefile)) and configures local Hugging Face / PyTorch cache
directories so model downloads stay inside the project's cache folder
instead of the user's home directory.

### Running the pipeline

```sh
make run
```

This runs the pipeline with the default data files:

- `data/input/functions_definition.json`: available function definitions
- `data/input/function_calling_tests.json`: prompts to run through the model
- `data/output/function_calling_results.json`: where results are written

Custom files can be passed like this:

```sh
make run DEFS=path/to/defs.json INPUT=path/to/input.json OUTPUT=path/to/output.json
```

Or directly with the module entrypoint:

```sh
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

### Testing

```sh
make test       # run the test suite
make test-cov   # run tests with a coverage report
```

### Linting / formatting

```sh
make lint
make format
```

## Algorithm explanation

The constrained decoding approach has two stages, both built around the idea
of only ever letting the model pick from a set of tokens that are known to
be valid:

1. **Function name selection** ([src/agentics/trie.py](src/agentics/trie.py),
   `handle_name` in [src/agentics/prompts.py](src/agentics/prompts.py)): all
   candidate function names are tokenized and inserted into a trie
   (`build_trie`). At each decoding step, `allowed_next_tokens` walks the
   trie using the tokens generated so far and returns only the token ids
   that still lead to a valid, complete function name. The model's logits
   are then restricted to that set (`constrained_next_token`), so it is
   physically impossible for the model to produce a function name that does
   not exist in the provided definitions. Decoding stops as soon as the
   trie reaches a marked end node (`is_end`).

2. **Parameter generation** (`handle_params`): once a function is selected,
   its parameter schema is walked one parameter at a time. For each
   parameter, the model generates tokens until it emits one of a small set
   of delimiter characters (`BLACKLIST`/`REGEX_BLACKLIST`, e.g. `,`, `}`,
   quotes), and the raw text collected so far is validated and coerced
   against the parameter's declared type (`_validate_param_value`): booleans
   must be `True`/`False`, numbers/integers must parse with `float`/`int`,
   strings must be non-empty. This keeps the output schema-correct without
   requiring a full grammar-constrained decoder.

Both stages cap the number of decoding steps (64) to guarantee termination
even if the model never produces a valid stopping token, raising a
descriptive error instead of looping forever.

## Design decisions

- **Trie-based constraint instead of a full grammar**: a trie is enough to
  constrain function names (a finite, known vocabulary) while keeping the
  implementation simple; a full constrained-decoding grammar engine would
  be overkill for this scope.
- **Pydantic models as the single source of truth for shapes**
  ([src/models.py](src/models.py)): `FunctionDefinition`, `ParameterDefinition`,
  `ReturnDefinition`, `PromptInput`, `FunctionCall` and `FunctionCallResult`
  describe every data shape that flows through the pipeline. The parser
  ([src/parsing/parser.py](src/parsing/parser.py)) validates raw JSON input
  through these models instead of hand-rolled schema checks, so validation
  rules live in one place and are reused for both input parsing and
  (potentially) output checking.
- **A dedicated exception hierarchy**
  ([src/errors/types.py](src/errors/types.py)): every failure mode (bad
  JSON, bad schema, missing function, bad parameter type, model load
  failure, cache setup failure, output write failure, ...) has its own
  `CallMeMaybeError` subclass. This lets the pipeline tell expected,
  recoverable errors (reported per-prompt as an `"error"` entry in the
  output) apart from truly unexpected ones, while still never crashing the
  whole run for a single bad prompt.
- **Per-prompt error isolation** ([src/call_me_maybe.py](src/call_me_maybe.py)):
  the main loop catches errors around each individual prompt so that one bad
  prompt (unknown function, malformed parameter, timeout) produces an
  `"error"` entry in the output JSON instead of aborting the entire batch.

## Performance analysis

- **Accuracy**: because function names and parameter types are constrained
  by construction, the pipeline cannot select a non-existent function or
  emit a type-mismatched value that passes validation — the model only
  influences *which* valid option is picked, not whether the output is
  well-formed. The main source of inaccuracy is the model choosing the
  wrong function or a semantically wrong (but type-valid) parameter value,
  which is a model-quality limitation rather than a pipeline bug.
- **Speed**: generation is done token-by-token with no batching, and a
  small decode cache (`decode_cache`) avoids re-decoding the same token id
  repeatedly during parameter generation. Using a small model
  (`Qwen/Qwen3-0.6B`) keeps per-token latency low; the step cap (64 tokens
  per phase) bounds worst-case latency per prompt.
- **Reliability**: every file read, JSON parse, schema check, model call and
  output write is wrapped in a specific exception type and handled either
  locally (continue with the next prompt) or at the CLI boundary (clean
  exit code and message on stderr). The program is designed to never raise
  an unhandled exception to the user.

## Challenges faced

- **Keeping generation bounded**: an unconstrained generation loop could run
  forever if the model never emits a delimiter or trie end token. This was
  solved with an explicit step limit (64) on both the function-name and
  parameter loops, raising a clear timeout-style error instead of hanging.
- **Validating generated values against their declared type**: LLM output
  is just text, so `_validate_param_value` has to parse/convert the
  collected text into the right Python type and raise a precise error when
  it doesn't match, rather than silently accepting malformed values.
- **Avoiding a single bad prompt from crashing the whole batch**: this
  required careful placement of `try`/`except` blocks around each prompt
  in the main loop, as well as a project-specific exception hierarchy so
  "expected" failures could be reported inline in the output.

## Testing strategy

- [tests/test_models.py](tests/test_models.py) exercises every pydantic
  model in isolation: valid cases, invalid types, empty values, JSON
  round-trips, and dict-based construction.
- [tests/test_real_data.py](tests/test_real_data.py) validates the actual
  project data files (`data/input/functions_definition.json`,
  `data/input/function_calling_tests.json`) against the pydantic models, to
  make sure the schemas stay in sync with real data.
- [tests/conftest.py](tests/conftest.py) provides reusable fixtures (sample
  functions, prompts, calls and results) shared across test modules.
- Tests are run with `pytest` (`make test` / `make test-cov`), configured in
  [pytest.ini](pytest.ini).

## Example usage

Running the full pipeline with the bundled sample data:

```sh
make run
```

Example input prompt ([data/input/function_calling_tests.json](data/input/function_calling_tests.json)):

```json
{
  "prompt": "What is the product of 3 and 5?"
}
```

Example matching function definition
([data/input/functions_definition.json](data/input/functions_definition.json)):

```json
{
  "name": "fn_multiply_numbers",
  "description": "Multiply two numbers together and return their product.",
  "parameters": {
    "a": { "type": "number" },
    "b": { "type": "number" }
  },
  "returns": { "type": "number" }
}
```

Example resulting output entry
(written to `data/output/function_calling_results.json`):

```json
{
  "prompt": "What is the product of 3 and 5?",
  "name": "fn_multiply_numbers",
  "parameters": { "a": 3.0, "b": 5.0 }
}
```

If something goes wrong for a given prompt (e.g. the model fails to settle
on a known function within the step limit), that entry becomes an error
object instead of aborting the whole run:

```json
{ "error": "FunctionSelectionError: Function name selection exceeded 64 steps. Selected: ''" }
```

## Resources

- [Pydantic documentation](https://docs.pydantic.dev/) — data validation
  and schema modeling
- [Hugging Face Transformers documentation](https://huggingface.co/docs/transformers)
  — loading and running causal language models locally
- [Hugging Face Hub documentation](https://huggingface.co/docs/hub) — model
  downloading and caching
- Qwen model card: [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B)
- Background reading on constrained / guided decoding (restricting language
  model output to a valid token subset), applied here through a
  hand-written trie rather than an external grammar library
- [pytest documentation](https://docs.pytest.org/) — testing framework used
  for the test suite

### Use of AI

An AI coding assistant (GitHub Copilot, Claude Sonnet model) was used during
this project for:

- Refactoring and tightening error handling across the pipeline (adding
  specific exception types, wrapping file I/O, model loading and output
  writing in `try`/`except` blocks so the program never crashes
  unexpectedly).
- Wiring the JSON parser ([src/parsing/parser.py](src/parsing/parser.py)) to
  validate input data through the existing pydantic models instead of
  hand-written schema checks.
- Reviewing the codebase for edge cases (e.g. empty prompt lists, malformed
  JSON, unbounded generation loops) and readability/organization
  improvements.
- Cleaning up and rewriting code comments/docstrings for clarity.
- Drafting this README based on the existing code and project structure.

The `src/llm_sdk` package (the local LLM wrapper) was not modified as part
of this work and is used as provided.

