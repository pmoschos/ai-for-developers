from argparse import ArgumentParser
from code_gen import ask, clean_code_output, save_code
from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT


def generate_code(description: str, with_tests: bool = False, save: str = None) -> dict:
    """Generate Python code and optionally tests without printing by default."""
    code = clean_code_output(ask(CODE_GENERATION_PROMPT.format(description=description)))
    result = {"code": code}

    if with_tests:
        result["tests"] = clean_code_output(ask(TEST_GENERATION_PROMPT.format(code=code)))

    if save:
        save_code(result["code"], save, result.get("tests"))

    return result


def display_result(result: dict):
    """Print generated code and optional tests."""
    print("\n=== Generated Code ===")
    print(result["code"])

    if "tests" in result:
        print("\n=== Unit Tests ===")
        print(result["tests"])


def interactive_mode():
    """Run an interactive prompt loop for code generation: input → generate → display → save? → repeat"""
    print()
    print("Interactive mode. Press Enter on an empty prompt to exit.")

    while True:
        description = input("\nDescribe the Python function to generate: ").strip()
        if not description:
            print("Exiting interactive mode.")
            return

        with_tests = input("Generate tests too? [y/N]: ").strip().lower() in {"y", "yes"}
        result = generate_code(description, with_tests=with_tests)

        display_result(result)

        save_choice = input("\nSave the result to a file? [y/N]: ").strip().lower()
        if save_choice in {"y", "yes"}:
            filename = input("Filename: ").strip()
            if filename:
                save_code(result["code"], filename, result.get("tests"))
            else:
                print("Skipping save because no filename was provided.")

def build_parser() -> ArgumentParser:
    """Create the CLI argument parser."""
    parser = ArgumentParser(description="Generate Python code from a natural-language description.")
    parser.add_argument(
        "description",
        nargs="?",
        help="Natural-language description of the Python function to generate.",
    )
    parser.add_argument(
        "--with-tests",
        action="store_true",
        help="Generate pytest unit tests using prompt chaining.",
    )
    parser.add_argument(
        "--save",
        metavar="FILE",
        help="Save the generated code to a file.",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode.",
    )
    return parser


def main():
    """Run the CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    if args.interactive or not args.description:
        interactive_mode()
        return

    print(f"Generating code from input: '{args.description}'")
    result = generate_code(args.description, with_tests=args.with_tests, save=args.save)
    display_result(result)


if __name__ == "__main__":
    main()