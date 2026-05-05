from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT

load_dotenv(override=True)

client = OpenAI()

def generate_code(description: str,with_tests: bool = False,save: Optional[str] = None,) -> dict[str, str]:
    """Generate Python code from a natural-language description.

    Args:
        description: A natural-language description of the desired function.
        with_tests: Whether to generate pytest tests for the produced code.
        save: An optional filename used to persist the generated output.

    Returns:
        A dictionary containing the generated code and, when requested, tests.
    """
    prompt = CODE_GENERATION_PROMPT.format(description=description)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2,
    )
    code = clean_code_output(response.choices[0].message.content)
    result: dict[str, str] = {"code": code}

    if with_tests:
        test_prompt = TEST_GENERATION_PROMPT.format(code=code)
        test_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=800,
            temperature=0.2,
        )
        result["tests"] = clean_code_output(test_response.choices[0].message.content)

    if save is None:
        print("=== Generated Code ===")
        print(result["code"])
        if "tests" in result:
            print("\n=== Unit Tests ===")
            print(result["tests"])
            
    if save:
        filename = save if save.endswith(".py") else f"{save}.py"
        save_code(result["code"], filename, result.get("tests"))

    return result


def clean_code_output(code: str) -> str:
    """Strip markdown code fences from model output."""
    cleaned_code = code.strip()
    if cleaned_code.startswith("```python"):
        cleaned_code = cleaned_code[9:]
    if cleaned_code.startswith("```"):
        cleaned_code = cleaned_code[3:]
    if cleaned_code.endswith("```"):
        cleaned_code = cleaned_code[:-3]
    return cleaned_code.strip()


def save_code(code: str, filename: str, tests: Optional[str] = None) -> None:
    """Save generated code and optional tests to a Python file.

    Args:
        code: The generated Python code.
        filename: The destination file path.
        tests: Optional pytest test code to append to the file.
    """
    filepath = Path(filename)
    full_code = code
    if tests:
        full_code = f"{code}\n\n\n# ==================== TESTS ====================\n\n{tests}"

    filepath.write_text(full_code, encoding="utf-8")
    print(f"Saved to {filepath.absolute()}")


def main() -> None:
    """Run a few sample code-generation requests."""
    print()
    print("=" * 48)
    print("Code Generator Demo")
    print("=" * 48)
    print()

    print("Example 1: Basic code generation")
    generate_code("a function that finds prime numbers up to n")

    print("\n" + "=" * 50 + "\n")

    print("Example 2: Code generation with tests")
    generate_code("merge two sorted lists", with_tests=True)

    print("\n" + "=" * 50 + "\n")

    print("Example 3: Save output to a file")
    generate_code("calculate fibonacci", save="fibonacci.py")


if __name__ == "__main__":
    main()
