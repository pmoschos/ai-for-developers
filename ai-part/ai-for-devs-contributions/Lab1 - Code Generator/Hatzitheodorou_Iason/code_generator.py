from ast import arg
#from cgi import test #Deprecated, not used
import os
from pathlib import Path
import re
import sys
from dotenv import load_dotenv
from openai import OpenAI
import argparse

"""Code Generator - CLI Version
=============================="""

# Load .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)

# Check that the env was loaded correctly
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

client = OpenAI()

# Import system prompts
from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT
prompt_list = [CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT]
for prompt in prompt_list:
    if not prompt or not isinstance(prompt, str):
        raise ValueError("One of the prompts is missing or not a string. Please check the prompts.py file.")

# ─────────────────────────────────────────────────────────────
# Helper function for validating filenames
# ─────────────────────────────────────────────────────────────

def validate_filename(filename: str) -> str:
    """
    Validates and sanitizes a filename to ensure it is safe for use.
    Args:
        filename: The input filename to validate
    Returns:
        A sanitized filename with a .py extension if valid, otherwise raises ValueError.
    Raises:
        ValueError: If the filename is invalid (e.g., contains prohibited characters).
    """
    # Ensure correct file extension
    if not filename.endswith(".py"):
        # Remove any existing extension and add .py
        filename = re.sub(r'\.\w+$', '', filename) + ".py"
    
    # Ensure the filename is valid (basic check)
    if not re.match(r'^[\w\-. ]+$', filename):
        raise ValueError("Invalid filename. Use only letters, numbers, underscores, hyphens, dots and spaces.")
    
    return filename

# ─────────────────────────────────────────────────────────────
# Define functions for code generation, test generation, and saving to file
# ─────────────────────────────────────────────────────────────
def generate_code(description: str, 
                  with_tests: bool = False, 
                  save_filename: str = None,
                  tests_filename: str = None,
                  model: str = "gpt-4o-mini",
                  client: OpenAI = client,
                  max_tokens: int = 800,
                  temperature: float = 0.2) -> dict:
    """
    Generates python code from natural language description, using a model
    compatible with the OpenAI API. Optionally generates unit tests 
    (Prompt Chaining) and saves to file.
    Args:
        description: Natural language description (e.g., "a function that sorts a list")
        with_tests: If True, generates unit tests (Prompt Chaining!)
        save_filename: If a filename is provided, saves the code
        tests_filename: If a filename is provided, saves the tests
        model: Which model to use for code generation (default: "gpt-4o-mini")
        client: OpenAI API compatible client instance (default: OpenAI client)
        max_tokens: Max tokens for the response (default: 800)
        temperature: Sampling temperature for generation (default: 0.2)
    Returns:
        dict: {"code": "...", "tests": "..."} (tests only if with_tests=True)
    """

    #Validate temperature
    if not (0.0 <= temperature <= 1.0):
        raise ValueError("Temperature must be between 0.0 and 1.0")
    
    #Validate max_tokens
    if max_tokens <= 0:
        raise ValueError("max_tokens must be a positive integer")

    if not with_tests:
        # Insert the description into the code generation prompt
        print(f"Generating code for: \n{description}")
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

    else:
        # Repetitive code block
        print(f"Generating code for: \n{description}")
        gen_prompt = CODE_GENERATION_PROMPT.format(description=description)

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": gen_prompt}],
            max_tokens=max_tokens,
            temperature=temperature    # low temperature for code generation
        )
        # Repetitive code block end

        code = response.choices[0].message.content
        code = clean_code_output(code)
        result = {"code": code}

        # Insert the generated code into the test generation prompt
        print(f"Generating tests for the code.")
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

    if save_filename:
        save_filename = validate_filename(save_filename)
        save_code(result.get("code", ""), save_filename)

    if tests_filename:
        tests_filename = validate_filename(tests_filename)
        save_code(result.get("tests", ""), tests_filename)

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
    # Validate and sanitize the filename
    filename = validate_filename(filename)
    
    filepath = Path(filename)
    if tests:
        full_code = f"{code}\n\n\n# ==================== TESTS ====================\n\n{tests}"
    else:
        full_code = code
    filepath.write_text(full_code)
    print(f"Saved to {filepath.absolute()}")

# ─────────────────────────────────────────────────────────────
# Define interactive mode function
# ─────────────────────────────────────────────────────────────

def interactive_mode(with_tests_argu: bool):
    """Runs the code generator in interactive mode, prompting the user 
    for input until they choose to exit.
    Args:
        with_tests_argu: Whether to generate tests for the code (True/False)
    Returns:
        None
    """
    print("Running code generator in interactive mode.")
    
    while True:
        user_input = input("\nEnter code description (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            print("Exiting interactive mode.")
            break
        else:
            description = user_input.strip()
            if description:
                # Generate code response
                result = generate_code(description, with_tests=with_tests_argu)
                
                print(f"\nGenerated Code:\n{result['code']}")
                print(f"\n{'_'*50}\n")
                # If test were generated, print them as well
                if with_tests_argu and "tests" in result:
                    print(f"\nGenerated Tests:\n{result['tests']}")
                    print(f"\n{'_'*50}\n")
                # Prompt to save the code to a file
                save_input = input("Do you want to save this code to a file? (y/n): ")
                if save_input.lower() == 'y':
                    filename = input("Enter the filename (e.g., 'prime.py'): ")
                    filename = validate_filename(filename)
                    save_code(result['code'], filename, result.get('tests'))
                elif save_input.lower() == 'n' :
                    print(f"\nCode not saved.")
                    print(f"\n{'='*50}\n")
                else:
                    print(f"\nInvalid input. Code not saved.")
                    print(f"\n{'='*50}\n")
    
    return None

# ─────────────────────────────────────────────────────────────
# Define CLI argument parsing
# ─────────────────────────────────────────────────────────────

def define_cli_args():
    """Defines the command-line arguments for the code generator CLI.
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description='Generate Python code based on a description.')
    parser.add_argument('description_text', nargs='*', help='Optional positional description of the code to generate')
    parser.add_argument('--description', type=str, help='A description of the code to generate')
    parser.add_argument('--with-tests', action='store_true', help='Whether to generate tests for the code')
    parser.add_argument('--temperature', type=float, nargs='?', default=0.2, help='Sampling temperature for generation, optional (default: 0.2)')
    parser.add_argument('--model', type=str, nargs='?', default="gpt-4o-mini", help='Which model to use for generation, optional (default: gpt-4o-mini)')
    parser.add_argument('--max-tokens', type=int, nargs='?', default=800, help='Max tokens for the response, optional (default: 800)')
    parser.add_argument('--save', type=str, default=None, help='Save the generated code to a file with the given filename (e.g., "prime.py")')
    parser.add_argument('--save_tests_only', type=str, default=None, help='Whether to save the generated tests to the file only')
    parser.add_argument('--save_all', type=str, default=None, help='Whether to save both code and tests to the file (if tests are generated) - one file name needed, the tests will be filename_tests.py')
    parser.add_argument('--display', action='store_true', help='Whether to display the generated code in the console')
    parser.add_argument('-i', action='store_true', help='Whether to generate code interactively')
    return parser.parse_args()

# ─────────────────────────────────────────────────────────────
# main()
# ─────────────────────────────────────────────────────────────
import sys
def main():
    ### Prompt Specificity Experiment
    # Experiment 1 - Vague Description
    # This will generated a very basic abstract scaffold sort function for a list
    # of elements of the same type, without any specific sorting algorithm implemented.
    #sys.argv = ['code_generator.py', '--description', 'a sort function', '--display']
    # Experiment 2 - More Specific Description
    # This will generate a more complete implementation of a sort function, using the quicksort algorithm.
    sys.argv = ['code_generator.py', '--description', 'a function that implements quicksort with in-place partitioning for a list of integers', '--display']
    # So clearly the user must be as specific as possible in their description of the
    # desired code, otherwise the LLM will not produce the desired output; garbage in, garbage out.
    
    # Get CLI arguments
    args = define_cli_args()
    positional_description = ' '.join(args.description_text).strip()
    description = args.description or positional_description

    if args.description and positional_description:
        print("Please provide the description either as positional text or with --description, not both.")
        return

    if args.i:
        interactive_mode(with_tests_argu=args.with_tests)
    else:
        if description:
            # Handle the saving logic based on the different save flags and validate                     
            filename = None
            tests_filename = None

            save_mode = (isinstance(args.save, str), isinstance(args.save_tests_only, str), isinstance(args.save_all, str), args.with_tests)

            match save_mode:
                case (True, False, False, _):
                    filename = validate_filename(args.save)
                case (False, True, False, True):
                    tests_filename = validate_filename(args.save_tests_only)
                case (False, False, True, True):
                    filename = validate_filename(args.save_all)
                    tests_filename = filename.replace(".py", "_tests.py")
                case (True, True, False, True):
                    filename = validate_filename(args.save)
                    tests_filename = validate_filename(args.save_tests_only)
                case (_, True, _, False):
                    raise ValueError("Cannot save tests only if --with-tests is not set.")
                case (_, False, True, False):
                    raise ValueError("Cannot save all if --with-tests is not set.")
                case (False, False, False, False):
                    pass
                case _: # Other flags should pass without a check
                    pass
            
            result = generate_code(description, 
                                with_tests=args.with_tests, 
                                save_filename=filename if filename else None,
                                tests_filename=tests_filename if tests_filename else None,
                                model=args.model, 
                                max_tokens=args.max_tokens, 
                                temperature=args.temperature)
            if args.display:
                print(f"\n\n{'='*50}")
                print(f"\n\n**Generated Code**:\n\n{result['code']}\n\n")
                print(f"\n\n{'='*50}")
                if args.with_tests and "tests" in result:
                    print(f"\n{'='*50}\n")
                    print(f"\n**Generated Tests**:\n{result['tests']}")
        else:
            print("Please provide a code description as positional text, with --description, or use interactive mode (-i). Use --help for more options.")

if __name__ == "__main__":
    main()