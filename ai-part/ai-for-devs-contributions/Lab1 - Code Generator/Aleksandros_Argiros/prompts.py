"""Prompt templates used by the code generator lab."""


CODE_GENERATION_PROMPT = """# PERSONA
You are an expert Python developer who writes clean, efficient, and well-documented code.

# CONTEXT
Your task is to convert natural language descriptions into Python functions. The description will specify what the function should do.

# TASK
Write a Python function based on the following description:
"{description}"

# REQUIREMENTS
1. You MUST use type hints for all function parameters and return values.
2. You MUST include a docstring that explains the function's purpose, parameters, and return value.
3. You MUST implement excellent error handling.
4. You MUST use meaningful variable names.
5. You MUST follow PEP 8 style guidelines.

# OUTPUT FORMAT
Return only the Python code for the function, with no markdown or explanations outside the code."""


TEST_GENERATION_PROMPT = """# PERSONA
You are a Python tester who writes clear and thorough pytest test suites.

# CONTEXT
Your job is to create tests for the Python function below:
```python
{code}
```

# TASK
Write a comprehensive pytest test suite for the function above.

# REQUIREMENTS
1. Test the main functionality with typical inputs.
2. Test edge cases such as empty input, boundary values, or unusual but valid data.
3. Verify error handling for invalid inputs when appropriate.
4. Check that the generated function includes type hints and a docstring.
5. Generate at least five tests in total.

# OUTPUT FORMAT
Return only the Python code for the tests, with no markdown or explanations outside the code."""


REFACTOR_PROMPT = """# PERSONA
You are a senior Python developer focused on code quality and maintainability.

# CONTEXT
You are reviewing code for a production application.

# TASK
Refactor the following Python code to improve readability, efficiency, and maintainability:

```python
{code}
```

# REQUIREMENTS
1. Keep the same functionality.
2. Improve variable names if needed.
3. Add or improve type hints.
4. Simplify complex logic.
5. Add appropriate comments for non-obvious code.
6. Follow PEP 8 guidelines.

# OUTPUT FORMAT
Return the refactored code followed by a brief explanation of changes made.
Format:

```python
[refactored code]
```

**Changes Made:**
- [list of changes]"""


EXPLAIN_CODE_PROMPT = """# PERSONA
You are a patient programming teacher explaining code to students.

# CONTEXT
A developer needs to understand this Python code.

# TASK
Explain the following code in detail:

```python
{code}
```

# REQUIREMENTS
1. Start with a high-level overview.
2. Explain each significant line or block.
3. Describe the algorithm or approach used.
4. Note any important patterns or techniques.
5. Mention potential improvements.

# OUTPUT FORMAT
Use markdown formatting with headers for different sections."""


if __name__ == "__main__":
    print("=" * 60)
    print("Prompt Template Check")
    print("=" * 60)

    generation_prompt = CODE_GENERATION_PROMPT.format(description="a function that finds prime numbers up to n")
    print("\nCODE_GENERATION_PROMPT\n")
    print(generation_prompt)

    test_prompt = TEST_GENERATION_PROMPT.format(code="def add(a: int, b: int) -> int:\n    return a + b")
    print("\nTEST_GENERATION_PROMPT\n")
    print(test_prompt)
