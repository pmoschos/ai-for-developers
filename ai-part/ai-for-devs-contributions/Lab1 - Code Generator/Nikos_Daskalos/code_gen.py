from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT

# Φόρτωση .env
env_path = Path(__file__).resolve().parents[0] / ".env"
load_dotenv(env_path, override=True)

client = OpenAI()

def ask(prompt: str, temperature: float = 0.2, max_tokens: int = 800) -> str:
    """Send a prompt to the OpenAI API and return the generated response."""
    r = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens)
    return r.choices[0].message.content

def generate_code(description: str, with_tests: bool = False, save: str = None) -> dict:
    """Generate Python code from a natural-language description, with optional tests and saving."""

    print(f"Generating code for: {description}")
    code = clean_code_output(ask(CODE_GENERATION_PROMPT.format(description=description)))
    result = {"code": code}

    if with_tests:
        result["tests"] = clean_code_output(ask(TEST_GENERATION_PROMPT.format(code=code)))

    print("=== Generated Code ===")
    print(result["code"])
    if "tests" in result:
        print("\n=== Unit Tests ===")
        print(result["tests"])
    if save:
        save_code(result["code"], save, result.get("tests"))
    return result

def clean_code_output(code: str) -> str:
    """Remove Markdown code block markers from generated code when they are present."""
    code = code.strip()
    if code.startswith('```python'):
        code = code[len('```python'):]
    elif code.startswith('```'):
        code = code[len('```'):]

    if code.endswith('```'):
        code = code[:-len('```')]
    return code.strip()
        
def save_code(code: str, filename: str, tests: str = None) -> None:
    """Save generated code to a file and append tests when they are provided."""
    filepath = Path(filename)
    full_code = code
    if tests:
        full_code = f"{code}\n\n\n# ==================== TESTS ====================\n\n{tests}"
    
    filepath.write_text(full_code)
    print(f"Saved to {filepath.absolute()}")

# ─────────────────────────────────────────────────────────────
# ΔΟΣΜΕΝΟ: Παραδείγματα εκτέλεσης
# ─────────────────────────────────────────────────────────────
def main():
    """Run the three built-in code generation examples."""
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
