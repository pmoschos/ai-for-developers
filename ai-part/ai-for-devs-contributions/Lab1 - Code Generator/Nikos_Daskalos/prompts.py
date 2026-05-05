CODE_GENERATION_PROMPT = """# PERSONA
You are a senior Python developer with 10+ years of experience.
You always follow best practices and clean code principles.
You write high-quality, well-documented code.

# CONTEXT
You are helping developers create Python functions from natural-language descriptions.

# TASK
Implement a Python function based on the following natural-language description:
"{description}"

# REQUIREMENTS
1. Use type hints for all function parameters and the return value.
2. Write a docstring that includes Args and Returns, and give an example of how to use the function.
3. Always handle edge cases (empty strings, None, wrong types, etc.).
4. Use meaningful and self-explanatory variable names.
5. Follow PEP 8 style recommendations.

# OUTPUT FORMAT
Return the generated Python function. 
Return ONLY the Python code, nothing else."""
 

TEST_GENERATION_PROMPT = """# PERSONA
You are a Senior SDET (Software Development Engineer in Test) with 10+ years of experience. 
You specialize in Python testing.
You always follow testing best practices.

# CONTEXT
You are helping developers test the following Python code effectively and efficiently:
```python
{code}
```

# TASK
Write comprehensive unit tests with pytest.

# REQUIREMENTS
1. Test happy path cases.
2. Test edge cases (empty inputs, boundary values).
3. Test error handling.
4. Use descriptive test function names.
5. Implement at least 5 test cases.

# OUTPUT FORMAT
Return the generated Python test cases. 
Return ONLY the Python test cases, nothing else."""

# ─────────────────────────────────────────────────────────────
# TESTS: Τρέξτε αυτό το αρχείο μόνο του για οπτικό έλεγχο
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Οπτικός Έλεγχος Prompt Templates")
    print("=" * 60)

    # Test 1: CODE_GENERATION_PROMPT
    print("\n── CODE_GENERATION_PROMPT ──")
    test_prompt = CODE_GENERATION_PROMPT.format(
        description="a function that finds prime numbers up to n"
    )
    print(test_prompt)

    # Έλεγχος placeholder
    if "{description}" in test_prompt:
        print("\n❌ ΣΦΑΛΜΑ: Το {description} δεν αντικαταστάθηκε!")
    else:
        print("\n✅ Placeholder {description} αντικαταστάθηκε σωστά")

    # Έλεγχος format section
    if "TODO" in test_prompt:
        print("⚠️  Υπάρχουν ακόμα TODO — συμπληρώστε τα!")
    else:
        print("✅ Δεν υπάρχουν TODO")

    # Test 2: TEST_GENERATION_PROMPT
    print("\n── TEST_GENERATION_PROMPT ──")
    test_prompt2 = TEST_GENERATION_PROMPT.format(
        code="def add(a: int, b: int) -> int:\n    return a + b"
    )
    print(test_prompt2)

    if "{code}" in test_prompt2:
        print("\n❌ ΣΦΑΛΜΑ: Το {code} δεν αντικαταστάθηκε!")
    else:
        print("\n✅ Placeholder {code} αντικαταστάθηκε σωστά")

    if "TODO" in test_prompt2:
        print("⚠️  Υπάρχουν ακόμα TODO — συμπληρώστε τα!")
    else:
        print("✅ Δεν υπάρχουν TODO")

    print()
    print("💡 Τα prompts φαίνονται OK; Προχωρήστε στο Βήμα 2 (code_gen.py)")
