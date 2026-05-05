"""
Πείραμα: Σύγκριση Personalities & Temperature (Βήμα 5)
======================================================
Στέλνουμε το ΙΔΙΟ ερώτημα σε ΟΛΕΣ τις personalities
και συγκρίνουμε τις απαντήσεις side-by-side.

Επιπλέον, πειραματιζόμαστε με διαφορετικές τιμές temperature
για να δούμε πώς επηρεάζει τη δημιουργικότητα.

Εκτέλεση:
    python compare_personalities.py

Δεν χρειάζεται να αλλάξετε κάτι — απλά τρέξτε και παρατηρήστε!
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

#load_dotenv(Path(__file__).parent.parent.parent / ".env")
load_dotenv(Path.cwd() / ".env") # Modificate this path if the .env file isn't in the same file with the chatbot.py

claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
CLAUDE_MODEL = "claude-sonnet-4-6"

client = OpenAI()

PERSONALITIES_DIR = Path(__file__).parent / "personalities"


def load_all_personalities() -> dict:
    """Φορτώνει όλα τα personality JSON αρχεία"""
    personalities = {}
    for file in PERSONALITIES_DIR.glob("*.json"):
        if file.stem.startswith("sample"):
            continue
        
        with open(file) as f:
            data = json.load(f)
            personalities[file.stem] = data
    return personalities


def ask_openai(prompt: str, system: str, temperature: float = 0.7, max_tokens: int = 300) -> str:
    """Στέλνει ερώτημα στο OpenAI API"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def ask_anthropic(prompt: str, system: str | None = None, temperature: float= 0.7, max_resp_tokens: int= 800, ai_model: str= "claude-sonnet-4-6", output_format: str | None = None) -> None:
    """
    Send a prompt to Anthropic using the streaming Messages API and return
    the complete generated text.

    Args:
        prompt (str):
            The user prompt to send to the model.
        system (str | None, optional):
            Optional system instruction for the model. In the streaming API
            for this SDK version, it is converted into the required list format.
            Defaults to None.
        temperature (float, optional):
            Controls randomness of the response. Defaults to 0.7.
        max_resp_tokens (int, optional):
            Maximum number of tokens in the generated response. Defaults to 800.
        ai_model (str, optional):
            The model name to use. Defaults to "claude-sonnet-4-6".
        output_format (str | None, optional):
            Optional output format for the streaming API, if supported by the
            installed SDK version. Defaults to None.

    Returns: None
    """

    params = {
        "model": ai_model,
        "max_tokens" : max_resp_tokens,
        "temperature": temperature,
        "messages": [
            {'role': 'user', 'content': prompt}
        ],
    }

    if system:
        params["system"] = [{"type": "text", "text": system}]

    if output_format:
        params["output_format"] = output_format
    
    with claude_client.messages.stream(**params) as stream:
        answer = stream.get_final_text()
    
    return answer


# ═══════════════════════════════════════════════════════════════
# ΠΕΙΡΑΜΑ 1: Σύγκριση Personalities
# Στέλνουμε το ΙΔΙΟ ερώτημα σε κάθε personality
# ═══════════════════════════════════════════════════════════════
def experiment_1_compare_personalities():
    """Σύγκριση απαντήσεων μεταξύ personalities"""
    print()
    print("=" * 60)
    print("  ΠΕΙΡΑΜΑ 1: Σύγκριση Personalities")
    print("  Το ΙΔΙΟ ερώτημα → ΔΙΑΦΟΡΕΤΙΚΕΣ personalities")
    print("=" * 60)

    # Αυτό είναι το ερώτημα που θα στείλουμε σε ΟΛΟΥΣ
    test_question = "Explain what a Python decorator is."

    print(f"\n📝 Ερώτηση: \"{test_question}\"\n")

    personalities = load_all_personalities()

    if not personalities:
        print("❌ Δεν βρέθηκαν personalities! Βεβαιωθείτε ότι υπάρχουν .json αρχεία στο personalities/")
        return

    for name, persona in personalities.items():
        print(f"{'─' * 60}")
        print(f"🎭 {persona['name']}")
        print(f"   Temperature: {persona.get('temperature', 0.7)}")
        print(f"{'─' * 60}")

        response = ask_anthropic(
            prompt=test_question,
            system=persona["system_prompt"],
            temperature=persona.get("temperature", 0.7)
        )

        # Εμφάνιση απάντησης (max 500 chars)
        display = response[:2500] + "..." if len(response) > 500 else response
        print(f"\n{display}\n")

    print("=" * 60)
    print("  🔍 ΠΑΡΑΤΗΡΗΣΗ:")
    print("  To ΙΔΙΟ ερώτημα, ΔΙΑΦΟΡΕΤΙΚΕΣ απαντήσεις!")
    print("  Αυτή είναι η δύναμη του system prompt.")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════
# ΠΕΙΡΑΜΑ 2: Temperature Experiment
# Στέλνουμε το ΙΔΙΟ ερώτημα 3 φορές με ΔΙΑΦΟΡΕΤΙΚΕΣ temperatures
# ═══════════════════════════════════════════════════════════════
def experiment_2_temperature():
    """Πείραμα: πώς η temperature επηρεάζει τις απαντήσεις"""
    print()
    print("=" * 60)
    print("  ΠΕΙΡΑΜΑ 2: Temperature Experiment")
    print("  Το ΙΔΙΟ ερώτημα → ΔΙΑΦΟΡΕΤΙΚΕΣ temperatures")
    print("=" * 60)

    test_question = "Write a creative one-liner about programming."
    system = "You are a helpful assistant."

    temperatures = [0.0, 0.5, 1.0]

    print(f"\n📝 Ερώτηση: \"{test_question}\"")
    print(f"   System: \"{system}\"")
    print()

    for temp in temperatures:
        label = {0.0: "🧊 ΑΚΡΙΒΕΣ", 0.5: "⚖️ ΙΣΟΡΡΟΠΗΜΕΝΟ", 1.0: "🔥 ΔΗΜΙΟΥΡΓΙΚΟ"}
        print(f"{'─' * 60}")
        print(f"  Temperature: {temp}  ({label.get(temp, '')})")
        print(f"{'─' * 60}")

        # Στέλνουμε 3 φορές για να δείξουμε τη ΜΕΤΑΒΛΗΤΟΤΗΤΑ
        for i in range(3):
            response = ask_anthropic(
                prompt=test_question,
                system=system,
                temperature=temp,
                max_resp_tokens=100
            )
            display = response.strip().replace("\n", " ")
            print(f"  Απάντηση {i+1}: {display[:120]}")

        print()

    print("=" * 60)
    print("  🔍 ΠΑΡΑΤΗΡΗΣΕΙΣ:")
    print("  • temp=0.0 → Οι 3 απαντήσεις είναι (σχεδόν) ΙΔΙΕΣ")
    print("  • temp=0.5 → Μικρές διαφοροποιήσεις")
    print("  • temp=1.0 → Κάθε απάντηση είναι ΔΙΑΦΟΡΕΤΙΚΗ")
    print()
    print("  Η temperature ελέγχει πόσο 'τυχαία' είναι η")
    print("  επιλογή tokens κατά τη generation.")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print()
    print("╔═══════════════════════════════════════════════════════╗")
    print("║    🧪 Πειράματα: System Prompts & Temperature         ║")
    print("╚═══════════════════════════════════════════════════════╝")

    # Πείραμα 1: Σύγκριση personalities
    experiment_1_compare_personalities()

    print("\n\n")

    # Πείραμα 2: Temperature
    experiment_2_temperature()

    print("\n✅ Τα πειράματα ολοκληρώθηκαν!")
    print("   Συζητήστε τα αποτελέσματα με τον διδάσκοντα.\n")