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

# Check that the env was loaded correctly
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

client = OpenAI()

# Import prompts from Βήμα 1
from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT


# ─────────────────────────────────────────────────────────────
# ΑΣΚΗΣΗ: Υλοποιήστε τις 3 συναρτήσεις
# ─────────────────────────────────────────────────────────────

def generate_code(description: str, 
                  with_tests: bool = False, 
                  save: str = None,
                  model: str = "gpt-4o-mini",
                  client: OpenAI = client,
                  max_tokens: int = 800,
                  temperature: float = 0.2) -> dict:
    """
    Generates python code from natural language description, using a model
    with the OpenAI API. Optionally generates unit tests (Prompt Chaining) and saves to file.

    Args:
        description: Natural language description (e.g., "a function that sorts a list")
        with_tests: If True, generates unit tests (Prompt Chaining!)
        save: If a filename is provided, saves the code
        model: Which model to use for code generation (default: "gpt-4o-mini")
        client: OpenAI API compatible client instance (default: OpenAI client)
        max_tokens: Max tokens for the response (default: 800)
        temperature: Sampling temperature for generation (default: 0.2)
    Returns:
        dict: {"code": "...", "tests": "..."} (tests only if with_tests=True)
    """
    
    print(f"Generating code for: {description}")
    gen_prompt = CODE_GENERATION_PROMPT.format(description=description)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": gen_prompt}],
        max_tokens=max_tokens,
        temperature=temperature    # low temperature for code generation
    )
    code = response.choices[0].message.content
    code = clean_code_output(code)
    result = {"code": code}
    print("=== Generated Code ===")
    print(result["code"])

    if with_tests:
        test_prompt = TEST_GENERATION_PROMPT.format(code=code)
        test_response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        tests = test_response.choices[0].message.content
        tests = clean_code_output(tests)
        result["tests"] = tests

        if "tests" in result:
            print("\n=== Unit Tests ===")
            print(result["tests"])

    if save:
        save_code(result["code"], save, result.get("tests"))
        return result

def clean_code_output(code: str) -> str:
    """
   Removes markdown formatting from LLM output to extract clean Python code.
    Args:
        code: Raw output from the LLM
    Returns:
        str: Clean Python code
    Example:
        Input:
        ```python
        def add(a, b):
            return a + b    ```
        Output:
        def add(a, b):
            return a + b   
"""

    code = code.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()

def save_code(code: str, 
              filename: str, 
              tests: str = None):
    """
    Stores code (and optionally tests) in a .py file.
    Args:
        code: Python code
        filename: Filename (e.g., "prime.py")
        tests: Optional unit tests
    Returns:
        None (saves file to disk)
    """
    
    filepath = Path(filename)
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
    generate_code("a function that finds prime numbers up to n")

    print("\n" + "=" * 50 + "\n")

    # Παράδειγμα 2: Με tests (Prompt Chaining!)
    print("── Παράδειγμα 2: Με tests (Prompt Chaining) ──")
    generate_code("merge two sorted lists", with_tests=True)

    print("\n" + "=" * 50 + "\n")

    # Παράδειγμα 3: Με αποθήκευση
    print("── Παράδειγμα 3: Με αποθήκευση σε αρχείο ──")
    generate_code("calculate fibonacci", save="fibonacci.py")

    # Small Experiment with Temperature
    print("\n" + "=" * 50 + "\n")
    print("── Small Experiments With Temperature at 0.9 ──")
    generate_code("a function that finds prime numbers up to n", temperature=0.9)

    print("\n" + "=" * 50 + "\n")

    generate_code("merge two sorted lists", temperature=0.9, with_tests=True)

    print("\n" + "=" * 50 + "\n")

    print("── Παράδειγμα 3: Με αποθήκευση σε αρχείο ──")
    generate_code("calculate fibonacci", save="fibonacci.py", temperature=0.9)

    print("\n" + "=" * 50 + "\n")
    print("── Observations on Temperature ──")
    print("\nEven at higher temperature, the code, especially for small tasks is correct.\n"
    "For more complex tasks like the test suite creation, the higher temperature helps create different\n" \
    " tests. This is possibly a good way to increase coverage and niche edge cases in the tests./n/n"
    "Interestingly, at higher temperatures the code is less standardized, with more less conforming/n"
    "variable names.")

if __name__ == "__main__":
    main()
