"""
Code Generator — Βασική έκδοση (Βήμα 2)
========================================
Δημιουργεί Python functions από φυσική γλώσσα.

Χρησιμοποιεί:
- prompts.py (Βήμα 1) για τα prompt templates
- OpenAI API για τη δημιουργία κώδικα
- Prompt Chaining: κώδικας → tests

Εκτέλεση:
    python code_generator.py (με επιθυμητό description / flags)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import argparse as argp

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
    print(f"Generating code for: {description}")
    prompt = CODE_GENERATION_PROMPT.format(description=description)

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000
    )

    output_code = response.choices[0].message.content
    code = clean_code_output(output_code)   
    result = {"code": code}

    if with_tests:
        test_prompt = TEST_GENERATION_PROMPT.format(code=code)
        
        response_testing = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": test_prompt}],
            temperature=0.2,
            max_tokens=1000
        )

        output_testing = response_testing.choices[0].message.content
        testing_code = clean_code_output(output_testing)
        result["tests"] = testing_code

    if save:
        save_code(code=code, filename=save, tests=result.get("tests"))

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
    code = code.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif  code.startswith("```"):
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
        full_code = f"{code}\n\n\n# ==================== TESTS ====================\n\n{tests}"
    else: 
        full_code = code
    
    filepath.write_text(full_code)

    print(f"Saved to {filepath.absolute()}")


def interactive_mode(with_tests: bool = False, save: str = None): 
    """
    Follows the pattern: input, generate, display, save (optional), repeat.

    Ends with keyboard signal ctrl + C
    """
    while True:
        try:
            description = input("\nEnter a description or exit with ctrl+C:\n")
            result = generate_code(description, with_tests, save)
            print("~~~~ Generated Code ~~~~")
            print(result["code"])
            if with_tests:
                print("~~~~ Unit tests ~~~~")
                print(result["tests"])

        except KeyboardInterrupt:                   # signal ctrl + c
            print("Exiting interactive mode.")
            break

def main():

    parser = argp.ArgumentParser()
    parser.add_argument("description", nargs="?", help="Description of the prompt")
    parser.add_argument("-i", action="store_true", help="Set to interactive mode")
    parser.add_argument("--with-tests", action="store_true", help="Include tests")   # default to false
    parser.add_argument("--save", nargs="?", const=True, default=False, help="Save the output to specific file")  
                                          # save without a filename given, will be default output.py

    parsed_args = parser.parse_args()

    # default values
    tests = False
    filename = None
    input_prompt = None

    if parsed_args.with_tests:
        tests = True

    if parsed_args.save == True:      # first check if just flag given, default 'output.py'
        filename = "output.py"
    elif parsed_args.save:
        filename =  parsed_args.save  # a given filename

    if parsed_args.description:
        input_prompt = parsed_args.description

    # if flag -i go to interactive mode
    if parsed_args.i:
        print("interactive on")
        interactive_mode(tests, filename)
    # if there is no interactive mode AND no description
    elif not input_prompt:
        interactive_mode(tests, filename)
    else:
        output = generate_code(input_prompt, tests, filename)
        print("~~~~ Generated Code ~~~~")
        print(output["code"])
        if tests:
            print("~~~~ Unit tests ~~~~")
            print(output["tests"])

if __name__ == "__main__":
    main()


# Comments on Step 4a - Prompt quality
# python code_generator.py "a sort function" -- prompt 1
# python code_generator.py "a function that implements quicksort with in-place partitioning for a list of integers" -- prompt 2
# Σύγκριση αποτελεσμάτων:
# Με τη χρήση του prompt 1, έχουμε συνοπτικότερο κώδικα με χρήση της built-in συνάρτησης sorted(), η οποία επιστρέφει την sorted list χωρίς
# να έχει αλλάξει την αρχική.
# Με χρήση του prompt 2, γίνεται υλοποίηση του αλγορίθμου Quickshort, με αναδρομικό sorting υπο-λιστών. Η αρχική λίστα τροποποιείται. 
# Ο κώδικας του 2ου prompt είναι αρκετά αναλυτικός και επεξηγηματικός, ενώ με το prompt 1 δεν φαίνεται η υλοποίηση που οδηγεί στο αποτέλεσμα.
# Ωστόσο, απαιτεί την κατανόηση της αναδρομής και του partitioning. Επιπλέον, η built-in συνάρτηση χρησιμοποιεί πιθανώς υλοποίηση λογαριθμικού
# χρόνου, ενώ η quicksort είναι τάξης O(n^2).      


# Comments on Step 4b - Temperature experiment
# Ο κώδικας με υψηλή θερμοκρασία (0.9) είναι πιο "εκφραστικός", περιλαμβάνει πιο αναλυτικά σχόλια, στα tests δημιουργεί ξεχωριστές δοκιμές για 
# περιπτώσεις μεγάλων και αρνητικών αριθμών και έχει πιο αναλυτικά doc comments. Αντιθέτως, ο κώδικας με χαμηλή θερμοκρασία (0.2) είναι πιο 
# συνοπτικός και "αυστηρός". Ενώνει όλα τα tests σε μία συνάρτηση και έχει πιο σύντομα σχόλια.
# Με χαμηλή θερμοκρασία το μοντέλο είναι πιο ντετερμινιστικό  (επιλογή του πιο πιθανού token), καθώς με υψηλότερες τιμές θερμοκρασίας επιλέγονται 
# και λιγότερο πιθανές απαντήσεις (φαινομενική "δημιουργικότητα"). Στην παραγωγή, λοιπόν, κώδικα γίνεται χρήση χαμηλής θερμοκρασίας με σκοπό την
# παραγωγή ορθού κώδικα, με συνέπεια και χωρίς syntactic/semantic errors.
