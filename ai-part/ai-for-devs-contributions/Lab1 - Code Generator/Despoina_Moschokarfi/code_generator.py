import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)

client = OpenAI()

if client:
    print("Client is ready!")
    print("="*50)

from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT

# Examples of input

# python code_generator.py "description" --with-tests --save output.py

# Simple generation
# python code_generator.py "a function that reverses a string"

# With tests enabled
# python code_generator.py "binary search" --with-tests

# Saving in a file
# python code_generator.py "factorial" --save factorial.py

# Interactive mode
# python code_generator.py -i

def generate_code(description: str, with_tests: bool = False, save: str = None):
    """
    Generates python code based on a description given by the user.

    Args:
        description: Text based on what python code is to be generated (π.χ. "a function that sorts a list")
        with_tests: If true, also generate tests for the python code
        save: Given a filename, it saves python code in a file

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
        temperature=0.2    # Low temperature for code generation
    )
    
    code = response.choices[0].message.content

    clean_code_output(code)
    result = {"code": code}

    # Check for test if specified
    if with_tests==True:
        # Generate prompt for tests
        # print("Generating tests...")
        prompt_test = TEST_GENERATION_PROMPT.format(code=code)
        response_test = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_test}],
            max_tokens=800,
            temperature=0.2
        )
        tests = response_test.choices[0].message.content
        clean_tests = clean_code_output(tests)
        result = {"code": code, "tests": clean_tests}

    if save:
        save_code(result["code"], save, result.get("tests"))
    

def clean_code_output(code: str) -> str:
    """
    Removes markdown code blocks (```python ... ```) before output.

    Args:
        code: Raw output from LLM

    Returns:
        str: Clean Python code

    Example:
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
    Saves python code in a file.

    Args:
        code: python code
        filename: Name of python file (ex. "prime.py")
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

def interactive_mode():
    print("Starting interactive mode...")
    
    while True:
        description = input("Enter description of the python code you would like to generate: ")
        with_tests = bool(input("Would you like test generation as well? (True/False)"))
        save = input("Save code in a file? (Give ONLY file name if Yes.)")
        generate_code(description, with_tests, save)
        cont = input("Continue? (y/n)")
        if cont.strip() == "n":
            print("Exiting interactive mode...")
            break

def main():

    # argparse setup
    parser = argparse.ArgumentParser(
        prog='Code_Generator_App',
        description='Generates python code from a user given description')
    
    # python code desc
    parser.add_argument("description", nargs="?", help="Description for the code to be generated")

    # If true then run tests
    parser.add_argument("--with-tests", action="store_true", help="Enables testing on the generated python code")

    # Save on the specified file name
    parser.add_argument("--save", help="Given a filename, it saves the code in a file")

    # Enables interaction mode
    parser.add_argument("-i", "--interactive", help="Enables interaction mode", action="store_true")

    args = parser.parse_args()

    if args.interactive or not args.description:
        interactive_mode()

    if args.description:
        print(f"Description: {args.description}!")
        generate_code(args.description, args.with_tests, args.save)


if __name__ == "__main__":
    main()