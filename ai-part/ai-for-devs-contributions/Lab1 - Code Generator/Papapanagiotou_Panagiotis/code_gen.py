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
from IPython.display import display, Markdown, clear_output
 
from anthropic import Anthropic

# Φόρτωση .env
load_dotenv(Path.cwd() / ".env") # Modificate this path if the .env file isn't in the same file with the code_gen.py

claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
CLAUDE_MODEL = "claude-opus-4-6" 

if claude_client:
    print(f"Antropic client ready - using model {CLAUDE_MODEL}")


# API call function 
def ask_anthropic(prompt: str, system: str | None = None, temperature: float= 0.7, max_resp_tokens: int= 800, ai_model: str= "claude-sonnet-4-6", output_format: str | None = None) -> None:
    """
    Send a prompt to Anthropic using the streaming Messages API and return
    the complete generated text.

    Args:
        prompt (str):
            The user prompt to send to the model.
        system (str | None, optional):
            Optional system instruction for the model. In the streaming API
            for this SDK version, it is converted into the required list format.
            Defaults to None.
        temperature (float, optional):
            Controls randomness of the response. Defaults to 0.7.
        max_resp_tokens (int, optional):
            Maximum number of tokens in the generated response. Defaults to 800.
        ai_model (str, optional):
            The model name to use. Defaults to "claude-sonnet-4-6".
        output_format (str | None, optional):
            Optional output format for the streaming API, if supported by the
            installed SDK version. Defaults to None.

    Returns: None
    """

    params = {
        "model": ai_model,
        "max_tokens" : max_resp_tokens,
        "temperature": temperature,
        "messages": [
            {'role': 'user', 'content': prompt}
        ],
    }

    if system:
        params["system"] = [{"type": "text", "text": system}]

    if output_format:
        params["output_format"] = output_format
    
    with claude_client.messages.stream(**params) as stream:
        full_text = ""
        for text in stream.text_stream:
            full_text += text
            clear_output(wait=True)
            # display(Markdown(full_text)) # Only for this module need to be in comments.
    
    return full_text


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

    print(f"Generating code for: {description}")
    prompt = CODE_GENERATION_PROMPT.format(description=description)

    raw_code = ask_anthropic(prompt, temperature= 0.2, ai_model= CLAUDE_MODEL)
    code = clean_code_output(raw_code)
    result = {"code": code}

    if with_tests:
        print("Generating unit tests...")
        test_prompt = TEST_GENERATION_PROMPT.format(code=code)
        raw_tests = ask_anthropic(test_prompt, temperature=0.2, ai_model= CLAUDE_MODEL)
        tests = clean_code_output(raw_tests)
        result["tests"] = tests

    # ── Εμφάνιση αποτελεσμάτων ──
    print("=== Generated Code ===")
    print(result["code"])
    if "tests" in result:
         print("\n=== Unit Tests ===")
         print(result["tests"])
    if save:
         save_code(result["code"], save, result.get("tests"))
         print(f"\nFiles saved successfully to {save}")
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

    cleaned_code = code.strip()
    if cleaned_code.startswith("```python"):
        cleaned_code = cleaned_code.removeprefix("```python").removesuffix("```")
    if cleaned_code.startswith("```"):
        cleaned_code = cleaned_code.removeprefix("```").removesuffix("```")
    
    return cleaned_code.strip()


def save_code(code: str, filename: str, tests: str = None) -> None:
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


if __name__ == "__main__":
    main()