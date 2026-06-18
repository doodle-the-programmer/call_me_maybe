# Roadmap

## 1. Lock down the project shape

- Create the `src/` package that will be run with `uv run python -m src`.
- Keep `llm_sdk/` available alongside `src/` so the project can import the provided model wrapper without touching private SDK APIs.
- Confirm `pyproject.toml` includes only the dependencies you are allowed to use, especially `numpy` and `pydantic`.
- Make sure `.gitignore` excludes Python artifacts, virtual environments, cache folders, and generated outputs.

## 2. Define the data model first

- Use `pydantic` models for every class and structured payload.
- Model the input function definitions, prompts, function parameters, and final output records.
- Add validation for missing files, malformed JSON, unexpected keys, and wrong parameter types.
- Decide early how JSON schema errors should be reported so the program fails gracefully instead of crashing.

## 3. Build the loader and validator layer

- Read `functions_definition.json` and `function_calling_tests.json` from disk.
- Normalize and validate function signatures before any generation happens.
- Verify the CLI can accept custom `--functions_definition`, `--input`, and `--output` paths.
- Return clear user-facing error messages for missing files, invalid JSON, or unusable schemas.

## 4. Implement function selection

- Use the LLM to choose the function name, not heuristics.
- Prepare the prompt so the model sees the available function descriptions and argument shapes.
- Keep the selection step separate from argument extraction so each stage is easier to debug and test.
- Make the default model target Qwen/Qwen3-0.6B and confirm the code still works if a different compatible model is swapped in.

## 5. Implement constrained decoding

- Read the vocabulary file from `llm_sdk` and map token IDs to text.
- Build the decoding loop so invalid tokens are masked out instead of relying on the model to emit perfect JSON.
- Enforce both JSON syntax and the expected schema for the selected function.
- Handle numeric, string, and boolean arguments explicitly so the output always stays parseable.

## 6. Wire the end-to-end pipeline

- For each prompt, generate exactly one output object with `prompt`, `name`, and `parameters`.
- Validate the model output before writing it to disk.
- Save results to `data/output/function_calling_results.json` by default.
- Keep the program resilient if a single prompt fails so one bad item does not take down the whole batch.

## 7. Add tests before polishing

- Add unit tests for JSON parsing, schema validation, and output formatting.
- Add edge-case tests for empty prompts, malformed function definitions, missing files, and weird argument values.
- Add small program tests that exercise the full flow with controlled sample inputs.
- Do not submit tests if the assignment does not require them, but keep them in the repo for confidence.

## 8. Finish with quality checks

- Run `flake8 .` and `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`.
- If time permits, run the stricter mypy pass as well.
- Verify the output JSON is valid and matches the function definitions exactly.
- Check that the project still works from a clean environment using `uv sync` and the documented run command.

## Suggested Order

1. Create the `src/` package and the `pydantic` models.
2. Add file loading and error handling.
3. Implement LLM-driven function selection.
4. Add constrained decoding and JSON schema enforcement.
5. Write tests for the tricky edge cases.
6. Run linting, type checking, and a full sample execution.
