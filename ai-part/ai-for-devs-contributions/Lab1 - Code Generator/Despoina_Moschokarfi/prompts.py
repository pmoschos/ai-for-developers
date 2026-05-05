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
You are a computer science professor with 10 years of experience with a specialty in python programming language.

# CONTEXT
Context: Helping beginner python programmers create code. 

# TASK
Create a python function according to this description:
"{description}"

# REQUIREMENTS
1. Type hints σε parameters και return value
2. Docstring με Args, Returns, Example
3. Χειρισμός edge cases
4. Meaningful variable names
5. PEP 8 style

# OUTPUT FORMAT
Return ONLY code.
DO NOT return any explanation or put code in markdowns."""


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
You are an experienced python developer working on a python program tasked with running various tests.

# CONTEXT
Context: You are testing the following python code to ensure the program is working as expected.

```python
{code}
```

# TASK
Present comprehensive unit tests with pytest.

# REQUIREMENTS
Requirements:
1. Test normal/happy path cases
2. Test edge cases (empty inputs, boundary values)
3. Test error handling
4. Descriptive test function names
5. Present at least 5 test cases

# OUTPUT FORMAT
Return ONLY python code.
DO NOT return any explanations."""


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
