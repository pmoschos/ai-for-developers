import argparse
from typing import Optional
from code_gen import generate_code


def interactive() -> None:
    """Prompt the user for generation inputs and execute one request."""
    input_description = input("Enter a natural language description of the code to generate: ").strip()
    with_tests = input("Generate unit tests as well? (y/n): ").strip().lower()
    save = input("Filename to save the generated code (or press Enter to skip): ").strip()

    if save and not save.endswith(".py"):
        save = f"{save}.py"

    generate_code(input_description, with_tests=with_tests == "y", save=save or None)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser for the generator."""
    parser = argparse.ArgumentParser(description="Generate Python code from a natural language description.")
    parser.add_argument("description", nargs="?", default=None, help="Natural language description of the code to generate")
    parser.add_argument("--with-tests", action="store_true", help="Also generate unit tests")
    parser.add_argument("--save", help="Filename to save the generated code")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    return parser


def main() -> None:
    """Run the command-line interface."""
    parser = build_parser()
    args = parser.parse_args()
    description: Optional[str] = args.description

    if args.interactive or description is None:
        while True:
            interactive()
            if input("Generate another? (y/n): ").strip().lower() != "y":
                print("Exiting.")
                break
        return

    generate_code(description, with_tests=args.with_tests, save=args.save)


if __name__ == "__main__":
    main()
