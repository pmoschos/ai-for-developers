import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import sys

# Φόρτωση .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)

client = OpenAI()

# Import prompts from Βήμα 1
from prompts import CODE_GENERATION_PROMPT, TEST_GENERATION_PROMPT

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

    if not description:
        raise ValueError("No description was provided")
    
    print(f"Generating code for: {description}")
    prompt = CODE_GENERATION_PROMPT.format(description=description)

    #Step 1 - Generate code snippet from description
    code = call_llm(prompt)
    code = clean_code_output(code)
    result = {'code':code}


    #Step 2 - Generate tests for the above code
    if with_tests and result.get('code', None): #Ensures both tests are enabled, and code snippet actually exists
        test_prompt = TEST_GENERATION_PROMPT.format(code=code)
        tests_raw = call_llm(test_prompt)
        tests_clean = clean_code_output(tests_raw)
        result["tests"] = tests_clean
    
    print("=== Generated Code ===")
    print(result["code"])
    if "tests" in result:
        print("\n=== Unit Tests ===")
        print(result["tests"])

    if save:
        save_code(result["code"], save, result.get("tests"))

        
    return result

    

def call_llm(prompt: str, max_tokens: int = 800, temperature: float = 0.2):
    """Call Open AI API and returns response"""
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages = [{'role':'user', 'content':prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content

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

    code = code.strip()
    if code.startswith("```python"):  
        code = code[9:]
    elif code.startswith("```"):       
        code = code[3:]

    if code.endswith("```"):          
        code = code[:-3]

        
    return code.strip()

def save_code(code: str, filename: str, tests: str = None):
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

def run_interactive_mode():
     # Βρόχος συνομιλίας
    while True:
        try:
            description_input = input("Describe your function: ")

            #check if description was provided
            if not description_input.strip():
                print("No description was given. Try again")
                continue

            #generate code
            result = generate_code(description_input)
            
            # check if code exists
            if result.get("code","").strip() == "":
                print("Unfortunately the code wasnt able to be generated")
                continue
            #ask for save
            save_input = input("Do you want to save this function? (y/n) ")
            #if yes, then save
            if save_input.strip().lower() == "y":
                save_file_name = input("How to name the file?")
                save_code(result.get("code"), filename=save_file_name)

            print(f"\n{'-'*50}\n")
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():

    parser = argparse.ArgumentParser()

    interactive_group = parser.add_argument_group("interactive mode")
    interactive_group.add_argument("-i", action="store_true", help="Run in interactive mode")
    if len(sys.argv) == 1 or "-i"  in sys.argv:
        run_interactive_mode()
    else:
        regular_group = parser.add_argument_group("regular mode")
        regular_group.add_argument("description", help="Description of function to be translated to python")
        regular_group.add_argument("--with-tests", help="Flag for tests", action='store_true')
        regular_group.add_argument("--save", metavar="FILE", help="File path to save in")

        args = parser.parse_args()
        generate_code(description=args.description, with_tests=args.with_tests, save= args.save)
 
if __name__ == "__main__":
    main()