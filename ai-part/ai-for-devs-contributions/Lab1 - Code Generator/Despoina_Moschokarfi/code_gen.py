"""
Code Generator — Βασική έκδοση (Βήμα 2)
========================================
Δημιουργεί Python functions από φυσική γλώσσα.

Χρησιμοποιεί:
- prompts.py (Βήμα 1) για τα prompt templates
- OpenAI API για τη δημιουργία κώδικα
- Prompt Chaining: κώδικας → tests

Εκτέλεση:
    python code_gen.py

Θα τρέξει 3 παραδείγματα αυτόματα.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Φόρτωση .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)

client = OpenAI()

# Import prompts from Βήμα 1
from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT


# ─────────────────────────────────────────────────────────────
# ΑΣΚΗΣΗ: Υλοποιήστε τις 3 συναρτήσεις
# ─────────────────────────────────────────────────────────────

def generate_code(description: str, with_tests: bool = False, save: str = None) -> dict:
    """
    Δημιουργεί Python κώδικα από περιγραφή σε φυσική γλώσσα.

    Args:
        description: Περιγραφή σε φυσική γλώσσα (π.χ. "a function that sorts a list")
        with_tests: Αν True, δημιουργεί και unit tests (Prompt Chaining!)
        save: Αν δοθεί filename, αποθηκεύει τον κώδικα

    Returns:
        dict: {"code": "...", "tests": "..."} (tests μόνο αν with_tests=True)
    """

    # Print the description
    print(f"Generating code for: {description}")

    # Generate prompt
    prompt = CODE_GENERATION_PROMPT.format(description=description)

    # API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2    # ← ΧΑΜΗΛΗ temperature για κώδικα!
    )
    
    code = response.choices[0].message.content

    clean_code_output(code)
    result = {"code": code}

    # Check for test if specified
    if with_tests==True:
        # Generate prompt for tests
        print("Generating tests...")
        prompt_test = TEST_GENERATION_PROMPT.format(code=code)
        response_test = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_test}],
            max_tokens=800,
            temperature=0.2    # ← ΧΑΜΗΛΗ temperature για κώδικα!
        )
        tests = response_test.choices[0].message.content
        clean_tests = clean_code_output(tests)
        result = {"code": code, "tests": clean_tests}

    # Results
    print("=== Generated Code ===")
    print(result["code"])
    if "tests" in result:
        print("\n=== Unit Tests ===")
        print(result["tests"])
    if save:
        save_code(result["code"], save, result.get("tests"))
    return result


def clean_code_output(code: str) -> str:
    """
    Αφαιρεί markdown code blocks (```python ... ```) από την έξοδο.

    Γιατί χρειάζεται:
      Τα LLMs συχνά τυλίγουν τον κώδικα σε markdown blocks,
      ακόμα κι αν το prompt λέει "no markdown"!

    Args:
        code: Raw output από το LLM

    Returns:
        str: Καθαρός Python κώδικας

    Παράδειγμα:
        Input:  '```python\\ndef add(a, b):\\n    return a + b\\n```'
        Output: 'def add(a, b):\\n    return a + b'
    """
    # strip code from whitespaces
    final_code = code.strip()

    # Clean code for each case
    if final_code.startswith("```python"):
        final_code = final_code[9:]
    
    if final_code.startswith("```"):
        final_code = final_code[3:]
        
    if final_code.endswith("```"):
        final_code = final_code[:-3]
    
    print(final_code)

    return final_code



def save_code(code: str, filename: str, tests: str = None):
    """
    Αποθηκεύει τον κώδικα σε αρχείο.

    Args:
        code: Ο κώδικας Python
        filename: Όνομα αρχείου (π.χ. "prime.py")
        tests: Optional unit tests
    """
    # Create filepath
    filepath = Path(filename)
    
    # Check if there are tests
    # else save just the code
    if tests:
        full_code = f"{code}\n\n\n# ==================== TESTS ====================\n\n{tests}"
    else:
        full_code = code

    filepath.write_text(full_code)
    print(f"Saved to {filepath.absolute()}")


# ─────────────────────────────────────────────────────────────
# ΔΟΣΜΕΝΟ: Παραδείγματα εκτέλεσης
# ─────────────────────────────────────────────────────────────
def main():
    """Τρέχει 3 παραδείγματα — τεστάρετε τις υλοποιήσεις σας!"""
    print()
    print("╔═══════════════════════════════════════════════╗")
    print("║         🐍 Code Generator — Βήμα 2            ║")
    print("╚═══════════════════════════════════════════════╝")
    print()

    # Παράδειγμα 1: Απλή δημιουργία
    print("── Παράδειγμα 1: Απλή δημιουργία ──")
    generate_code("a function that prints 'Hello from despoina'")

    print("\n" + "=" * 50 + "\n")

    # Παράδειγμα 2: Με tests (Prompt Chaining!)
    print("── Παράδειγμα 2: Με tests (Prompt Chaining) ──")
    generate_code("merge two sorted lists", with_tests=True)

    print("\n" + "=" * 50 + "\n")

    # Παράδειγμα 3: Με αποθήκευση
    print("── Παράδειγμα 3: Με αποθήκευση σε αρχείο ──")
    generate_code("calculate fibonacci", save="fibonacci.py")


if __name__ == "__main__":
    main()
