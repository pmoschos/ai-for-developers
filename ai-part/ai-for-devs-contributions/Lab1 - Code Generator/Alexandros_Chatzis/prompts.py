"""
Prompt Templates for Code Generator (Βήμα 1)
=============================================
Δομή prompts χρησιμοποιώντας το PCTF framework:
  P = Persona  (ρόλος AI)
  C = Context  (πλαίσιο)
  T = Task     (τι ζητάμε)
  F = Format   (μορφή εξόδου)

Δοκιμή:
    python prompts.py
"""


# ─────────────────────────────────────────────────────────────
# ΑΣΚΗΣΗ: Γράψτε το CODE_GENERATION_PROMPT
# ─────────────────────────────────────────────────────────────
#
# Αυτό το prompt θα δημιουργεί Python functions από περιγραφή.
# Χρησιμοποιεί placeholder: {description}
#
# Παράδειγμα χρήσης:
#   prompt = CODE_GENERATION_PROMPT.format(description="a function that sorts a list")
#
CODE_GENERATION_PROMPT = """# PERSONA
You are an expert Python developer with 10 years of experience.

# CONTEXT
You are helping developers generate code.

# TASK
Generate a Python function based on:
"{description}"

# REQUIREMENTS
1. Use type hints for all parameters and the return value
2. Include a clear docstring with Args, Returns, Raises, and Example
3. Validate input to ensure the range contains only non-negative integers and that the start is less than or equal to the end
4. Handle edge cases (e.g., empty range, large numbers, zero factorial)
5. Use efficient computation (avoid redundant calculations, e.g., reuse previous factorial results)
6. Raise meaningful exceptions for invalid input
7. Follow PEP 8 style guidelines
8. Use clear and descriptive variable names

# OUTPUT FORMAT
Return ONLY the Python code."""


# ─────────────────────────────────────────────────────────────
# ΑΣΚΗΣΗ: Γράψτε το TEST_GENERATION_PROMPT
# ─────────────────────────────────────────────────────────────
#
# Αυτό το prompt παίρνει ΚΩΔΙΚΑ (όχι description) και δημιουργεί tests.
# Χρησιμοποιεί placeholder: {code}
#
# Αυτό είναι PROMPT CHAINING:
#   Βήμα 1: description → CODE_GENERATION_PROMPT → κώδικας
#   Βήμα 2: κώδικας    → TEST_GENERATION_PROMPT  → tests
#
TEST_GENERATION_PROMPT = """# PERSONA
You are a Python testing expert.

# CONTEXT
You are writing tests for the following Python code

```python
{code}
```

# TASK
Write comprehensive unit tests με pytest

# REQUIREMENTS
1. Cover normal/happy path scenarios 
2. Test edge cases such as:
- start == end
- start == 0
- minimal ranges (e.g single value)
3. Test error handling:
- negative inputs
- start greater than end
4. Descriptive test function names
5. Include at least 5 test cases
6. Use pytest conventions
7. Ensure tests are independent and deterministic

# OUTPUT FORMAT
Return ONLY valid Python test code using pytest, without explanations or comments outside the code block."""


# ─────────────────────────────────────────────────────────────
# ΔΟΣΜΕΝΑ: Bonus prompts (παραδείγματα για μελέτη)
# ─────────────────────────────────────────────────────────────

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
1. Keep the same functionality
2. Improve variable names if needed
3. Add or improve type hints
4. Simplify complex logic
5. Add appropriate comments for non-obvious code
6. Follow PEP 8 guidelines

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
1. Start with a high-level overview
2. Explain each significant line or block
3. Describe the algorithm or approach used
4. Note any important patterns or techniques
5. Mention potential improvements

# OUTPUT FORMAT
Use markdown formatting with headers for different sections."""


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
        description="a function that computes factorials for a range of numbers"
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
        code="""def compute_factorials(start: int, end: int) -> List[int]:
'''
Computes the factorials for a range of non-negative integers.

Args:
    start (int): The starting number of the range (inclusive).
    end (int): The ending number of the range (inclusive).

Returns:
    List[int]: A list containing the factorials of the numbers from start to end.

Raises:
    ValueError: If start is greater than end, or if either start or end is negative.

Example:
    >>> compute_factorials(0, 5)
    [1, 1, 2, 6, 24, 120]
'''
if start < 0 or end < 0:
    raise ValueError("Both start and end must be non-negative integers.")
if start > end:
    raise ValueError("Start must be less than or equal to end.")

factorials = [1] * (end + 1)

for i in range(2, end + 1):
    factorials[i] = factorials[i - 1] * i

return factorials[start:end + 1]"""
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
