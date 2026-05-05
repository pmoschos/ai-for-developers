import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import argparse

# Φόρτωση .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)

client = OpenAI()

from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT


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
    
    prompt = CODE_GENERATION_PROMPT.format(description=description)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2    
    )
    
    code = response.choices[0].message.content

    code = clean_code_output(code)

    result = {"code": code}

    if with_tests:
        test_prompt = TEST_GENERATION_PROMPT.format(code=code)

        test_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=800,
            temperature=0.2
        )

        tests = test_response.choices[0].message.content
        tests = clean_code_output(tests)

        result["tests"] = tests


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


    code = code.strip()

    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]

    if code.endswith("```"):
        code = code[:-3]

    return code.strip()


def save_code(code: str, filename: str, tests: str = None):
    """
    Αποθηκεύει τον κώδικα σε αρχείο.

    Args:
        code: Ο κώδικας Python
        filename: Όνομα αρχείου (π.χ. "prime.py")
        tests: Optional unit tests
    """
    
    filepath = Path(filename)

    if tests:
        full_code = f"{code}\\n\\n\\n# ==================== TESTS ====================\\n\\n{tests}"
    else:
        full_code = code
    
    filepath.write_text(full_code)

    print(f"Saved to {filepath.absolute()}")


def interactive_mode():
    print("Interactive mode (type 'exit' to quit)\n")

    while True:
        description = input("Enter description: ")

        if not description.strip():
            print("Please enter a description.\n")
            continue

        if description.lower() in ["exit", "quit"]:
            break

        with_tests = input("Generate tests? (y/n): ").lower() == "y"

        result = generate_code(description, with_tests, save=None)

        save = input("Save to file? (filename or Enter to skip): ")

        if save:
            save_code(result["code"], save, result.get("tests"))

def main():
    parser = argparse.ArgumentParser(description="AI Code Generator")

    # positional argument
    parser.add_argument("description", nargs="?", help="Function description")

    # optional flags
    parser.add_argument("--with-tests", action="store_true", help="Generate unit tests")
    parser.add_argument("--save", type=str, help="Save to file")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    # Αν interactive mode
    if args.interactive:
        interactive_mode()
        return

    # Αν δεν υπάρχει description → μπpytrhες interactive
    if not args.description:
        interactive_mode()
        return

    # Κανονική εκτέλεση
    result = generate_code(
        args.description,
        with_tests=args.with_tests,
        save=args.save
    )

    print("\n=== Generated Code ===")
    print(result["code"])

    if "tests" in result:
        print("\n=== Unit Tests ===")
        print(result["tests"])

if __name__ == "__main__":
    main()