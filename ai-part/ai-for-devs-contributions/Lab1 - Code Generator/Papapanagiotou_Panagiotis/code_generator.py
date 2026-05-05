import argparse
import sys

from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT
from code_gen import ask_anthropic, clean_code_output, save_code

CLAUDE_MODEL = "claude-opus-4-6" 

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

    raw_code = ask_anthropic(prompt, temperature= 0.2, ai_model= CLAUDE_MODEL)
    code = clean_code_output(raw_code)

    result = {"code": code}

    if with_tests:
        test_prompt = TEST_GENERATION_PROMPT.format(code=code)
        raw_tests = ask_anthropic(test_prompt, temperature=0.2, ai_model= CLAUDE_MODEL)
        tests = clean_code_output(raw_tests)
        result["tests"] = tests

    if save:
         save_code(result["code"], save, result.get("tests"))
    
    return result

def interactive_mode() -> None:
    """Ask user for description and generate code."""

    print("Interactive Code Geerator (type 'exit or 'q' to quit)")

    while True:
        description = input("Describe the function that you want to create: ").strip()

        if description.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        if not description:
            print("Empty description. Try again.")
            continue

        test_choice = input("Generate tests? (y/n): ").strip().lower()
        with_tests = test_choice.startswith("y")

        save_choice = input("You want to save to file? (filename or 'n' if not)").strip()
        save = save_choice if save_choice.lower() != "n" else None

        try:
            result = generate_code(description, with_tests, save)

            print("=== Generated Code ===")
            print(result["code"])

            if with_tests and "tests" in result:
                print("\n=== Unit Tests ===")
                print(result["tests"])

            if save:
                print(f"\nFiles saved successfully to {save}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description= "Generate Python code from natural language descriptions",
        epilog= "Examples:\n"
               "  python code_generator.py 'function that checks if a number is prime'\n"
               "  python code_generator.py 'merge two sorted lists' --with-tests\n"
               "  python code_generator.py 'calculate fibonacci' --save fib.py\n"
               "  python code_generator.py -i"
    )

    parser.add_argument(
        "description",
        nargs="?",
        help="Description of the function to generate"
    )

    parser.add_argument(
        "--with-tests",
        action="store_true",
        help="Generate unit tests for the generative code"
    )

    parser.add_argument(
        "--save",
        metavar="FILENAME",
        help="Save the generated code to a Python file"
    )

    parser.add_argument(
        "-i",
        action="store_true",
        help="Run in interacive mode (press 'exit' or 'q' to quit)"
    )

    args = parser.parse_args()

    # Interactive mode
    if args.i:
        interactive_mode()

    # If not provide description
    if not args.description:
        parser.print_help()
        print("\nx Error: please provide a description or use -i for interactive mode")
        sys.exit(1)

    print(f"\n\nGenerating code for: {args.description}")
    if args.with_tests:
        print("Generating unit tests...")
    if args.save:
        print(print(f"\nFiles saving to {args.save}"))

    
    try:
        result = generate_code(args.description, args.with_tests, args.save)

        print()
        print("╔═══════════════════════════════════════════════╗")
        print("║          GENERATED 🐍 CODE                    ║")
        print("╚═══════════════════════════════════════════════╝")
        print()

        print(result["code"])

        if args.with_tests and "tests" in result:
            print("\n=== Generated Unit Tests ===")
            print(result["tests"])
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    main()