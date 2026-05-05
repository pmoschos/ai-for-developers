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
You are a Senior Python Developer with 11 years of experience specializing in clean and production-ready code.

# CONTEXT
You are assist a Python development team by generate CLEAR Python code based on natural language description to accelarate the prototyping phase. 

# TASK
Generate a robust Python function accord the following description:
"{description}"

# REQUIREMENTS
1. Include Type hints in the parameters and the return value Type
2. Properly Python Docstring with Args, Returns, mini Example
3. Handling edge cases.(e.g zero divs, empty inputs, invalid types) 
4. Meaningful and short Python variable and function names. (PEP 8 style)

# OUTPUT FORMAT
Return ONLY the raw Python code.
Do NOT include markdown code blocks. 

# OUTPUT Example
def sum_even_numbers(numbers: list) -> int:
    '''Return the sum of all even numbers in the given list.
    
    Args:
        numbers (list): List of integers.
    
    Returns:
        int: Sum of even numbers.
    '''
    return sum(num for num in numbers if num % 2 == 0)
"""


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
You are a Python expert tester.  

# CONTEXT
You are writing unit tests for the following Python code to ensure stability and reliability to production -ready programs.  

```python
{code}
```

# TASK
Generate a comprehensive unit tests using 'pytest' library. 

# REQUIREMENTS
1. Test normal/happy path cases
2. Test edge cases (empty inputs, boundary values)
3. Test error handling
4. Descriptive test function names
5. Minimum 5 test cases to ensure broad coverage. 

# OUTPUT FORMAT
Return ONLY the Python code for the tests.
Do NOT include markdown formatting, backticks, or any conversational text.
Start directly with 'import pytest'.

# OUTPUT Example
import pytest

# Test cases
def test_sum_even_numbers_basic():
    assert sum_even_numbers([1, 2, 3, 4, 5, 6]) == 12   # 2+4+6 = 12

def test_sum_even_numbers_only_even():
    assert sum_even_numbers([2, 4, 6, 8]) == 20

def test_sum_even_numbers_only_odd():
    assert sum_even_numbers([1, 3, 5, 7]) == 0

def test_sum_even_numbers_empty_list():
    assert sum_even_numbers([]) == 0

def test_sum_even_numbers_with_negatives():
    assert sum_even_numbers([-2, -1, 0, 1, 2]) == 0     # -2 + 0 + 2 = 0

"""


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