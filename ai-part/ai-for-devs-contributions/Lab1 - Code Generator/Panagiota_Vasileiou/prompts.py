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
You are a senior Software Engineer with 14 years of experience in code development, testing and deployment.

# CONTEXT
You are in charge of a development team and ensure the best outcome. You optimize the developers' functions and assist them when needed.

# TASK
"{description}"

# REQUIREMENTS
1. The variable names must be meaningful
2. Add comments when needed to explain something complex
3. Add doc comments
4. Handle edge cases

# OUTPUT FORMAT
Provide ONLY the output code. Use plain text and not Markdown or LaTex.
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
You are a Senior Developer, with 8 years of experience, specializing in code testing.

# CONTEXT
You need to create tests for the function following. It is important that you cover all the cases.

```python
{code}
```

# TASK
Using pytest, create comprehensive unit tests.
We need a complete set of unit tests for it, covering possible edge cases, exceptions that might happen and success scenarios.
We need to ensure that the function is correct. 

# REQUIREMENTS
1. Write tests that have a successful outcome and normal flow
2. Write tests that cover ALL possible edge cases
3. Test the way errors are being handled
4. Use meaningful variable names
5. Provide comments for complex parts
6. Provide comments (after declaring the function) of what we actually expect to happen

# OUTPUT FORMAT
Provide ONLY the output code, with NO further explanations. Use plain text and not Markdown or LaTex."""


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