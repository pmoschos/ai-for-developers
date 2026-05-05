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

import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent.parent / ".env")

client = OpenAI()

PERSONALITIES_DIR = Path(__file__).parent / "personalities"


def load_all_personalities() -> dict:
    """Φορτώνει όλα τα personality JSON αρχεία"""
    personalities = {}
    for file in PERSONALITIES_DIR.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            personalities[file.stem] = data
    return personalities


def ask(prompt: str, system: str, temperature: float = 0.7, max_tokens: int = 500) -> str:
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

        response = ask(
            prompt=test_question,
            system=persona["system_prompt"],
            temperature=persona.get("temperature", 0.7)
        )

        # Εμφάνιση απάντησης (max 800 chars)
        display = response[:800] + "..." if len(response) > 800 else response
        print(f"\n{display}\n")

    print("=" * 60)
    print("  🔍 ΠΑΡΑΤΗΡΗΣΗ:")
    print("  To ΙΔΙΟ ερώτημα, ΔΙΑΦΟΡΕΤΙΚΕΣ απαντήσεις!")
    print("  Αυτή είναι η δύναμη του system prompt.")
    print("  Note how style influences how the model approaches the\n" \
    " answer; some are quicker to provide the answer, others require\n" \
    " lengthier exposes of their style before providing the answer. This\n " \
    " of course affects token consumption and latency.")
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
            response = ask(
                prompt=test_question,
                system=system,
                temperature=temp,
                max_tokens=100
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
    print(" Low temperture -> more consistent, the most probable tokens are chosen more often\n" 
    " High temperature -> more variable, less probable tokens are chosen more often\n" )


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
