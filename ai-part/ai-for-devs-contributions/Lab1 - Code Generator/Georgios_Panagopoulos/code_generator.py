"""
Code Generator CLI — Βήμα 3
============================
CLI tool για δημιουργία Python functions από φυσική γλώσσα.

Χρήση:
    python code_generator.py "a function that sorts a list"
    python code_generator.py "merge two sorted lists" --with-tests
    python code_generator.py "calculate fibonacci" --save fib.py
    python code_generator.py -i
"""

import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Φόρτωση .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)

client = OpenAI()

from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT


def clean_code_output(code: str) -> str:
    code = code.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()


def generate_code(description: str, with_tests: bool = False, save: str = None) -> dict:
    prompt = CODE_GENERATION_PROMPT.format(description=description)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2,
    )
    code = clean_code_output(response.choices[0].message.content)
    result = {"code": code}

    if with_tests:
        test_prompt = TEST_GENERATION_PROMPT.format(code=code)
        test_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=800,
            temperature=0.2,
        )
        result["tests"] = clean_code_output(test_response.choices[0].message.content)

    if save:
        filepath = Path(save)
        if "tests" in result:
            full_code = (
                f"{result['code']}\n\n\n"
                f"# ==================== TESTS ====================\n\n"
                f"{result['tests']}"
            )
        else:
            full_code = result["code"]
        filepath.write_text(full_code)
        print(f"Saved to {filepath.absolute()}")

    return result


def interactive_mode():
    print("Code Generator — Interactive Mode")
    print('Type "quit" or "exit" to stop.\n')

    while True:
        description = input("Description: ").strip()
        if description.lower() in ("quit", "exit"):
            break
        if not description:
            continue

        print("Generating...")
        result = generate_code(description)

        print("\n=== Generated Code ===")
        print(result["code"])

        save_input = input("\nSave to file? (enter filename or press Enter to skip): ").strip()
        if save_input:
            filepath = Path(save_input)
            filepath.write_text(result["code"])
            print(f"Saved to {filepath.absolute()}")

        print()


def main():
    parser = argparse.ArgumentParser(description="Generate Python functions from natural language.")
    parser.add_argument("description", nargs="?", help="Description of the function to generate")
    parser.add_argument("--with-tests", action="store_true", help="Also generate unit tests")
    parser.add_argument("--save", metavar="FILE", help="Save generated code to this file")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.description:
        print(f"Generating code for: {args.description}")
        result = generate_code(args.description, with_tests=args.with_tests, save=args.save)
        print("\n=== Generated Code ===")
        print(result["code"])
        if "tests" in result:
            print("\n=== Unit Tests ===")
            print(result["tests"])
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
