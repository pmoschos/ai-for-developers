# 🎭 Εργαστηριακή Άσκηση: Personality Chatbot

## Περιγραφή Άσκησης

Σε αυτή την άσκηση θα υλοποιήσετε ένα **chatbot με εναλλασσόμενες προσωπικότητες** (personalities). Κάθε personality ορίζεται μέσω ενός **system prompt** σε αρχείο JSON και καθορίζει τον τρόπο που το AI απαντά στον χρήστη.

Θα δουλέψετε σε **5 βήματα** (αυξανόμενης δυσκολίας), ξεκινώντας από τη διαχείριση ιστορικού μηνυμάτων μέχρι τη δημιουργία web interface και πειράματα σύγκρισης.

---

## Στόχοι Μάθησης

Μετά την ολοκλήρωση αυτής της άσκησης θα κατανοείτε:

| Θέμα | Τι θα μάθετε |
|------|-------------|
| **System Prompts** | Πώς ένα system prompt ορίζει τη "συμπεριφορά" και "προσωπικότητα" ενός LLM |
| **Conversation Memory** | Πώς διατηρούμε μνήμη σε ένα chatbot (πέρνοντας ολόκληρο το ιστορικό σε κάθε API call) |
| **Temperature** | Πώς η παράμετρος temperature επηρεάζει τη δημιουργικότητα vs ακρίβεια |
| **OpenAI Chat API** | Πώς δομείται ένα API call (`messages`, `model`, `max_tokens`) |
| **Gradio** | Πώς φτιάχνουμε ένα web UI για AI εφαρμογές |

---

## Προαπαιτούμενα

- Python 3.10+
- Βιβλιοθήκες: `openai`, `python-dotenv`, `gradio`
- Αρχείο `.env` στον γονικό φάκελο με:
  ```
  OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
  ```

---

## Δομή Αρχείων

```
personality_chatbot_exe/
├── README.md                      ← Αυτό το αρχείο (εκφώνηση)
├── conversation_manager.py        ← Βήμα 1: Διαχείριση ιστορικού (+Bonus: export)
├── chatbot.py                     ← Βήμα 2: Κύρια λογική chatbot
├── gradio_app.py                  ← Βήμα 3: Web UI
├── compare_personalities.py       ← Βήμα 5: Πειράματα σύγκρισης (ΔΟΣΜΕΝΟ)
└── personalities/
    ├── cynical_support.json       ← ΔΟΣΜΕΝΟ (πλήρες παράδειγμα)
    ├── pirate_expert.json         ← Βήμα 4: Συμπληρώστε εσείς
    └── zen_master.json            ← Βήμα 4: Συμπληρώστε εσείς
```

> **Σημείωση:** Τα αρχεία που θα επεξεργαστείτε περιέχουν σχόλια `TODO` στα σημεία
> που χρειάζεται κώδικας. Τα τμήματα με σχόλιο `ΔΟΣΜΕΝΟ` δεν χρειάζονται αλλαγή.

---

## Βήμα 1: Conversation Manager — `conversation_manager.py`

### 🟢 Δυσκολία: Εύκολο | ⏱️ Εκτιμώμενος χρόνος: 15-20 λεπτά

### Θεωρητικό Υπόβαθρο

Τα LLMs (Large Language Models) **δεν έχουν μνήμη** μεταξύ κλήσεων API.
Σε κάθε request πρέπει να στείλουμε **ολόκληρο το ιστορικό** της συνομιλίας:

```python
messages = [
    {"role": "system",    "content": "You are a pirate..."},   # ← personality
    {"role": "user",      "content": "Hello!"},                # ← 1ο μήνυμα χρήστη
    {"role": "assistant", "content": "Ahoy, matey!"},          # ← 1η απάντηση AI
    {"role": "user",      "content": "Tell me about Python"},  # ← 2ο μήνυμα χρήστη
]
```

Η κλάση `ConversationManager` είναι υπεύθυνη για τη διατήρηση αυτού του ιστορικού.

### Τι πρέπει να υλοποιήσετε

| Μέθοδος | Τι κάνει | Γραμμές κώδικα |
|---------|----------|:--------------:|
| `set_system_prompt(prompt)` | Αποθηκεύει το system prompt | ~1 |
| `add_message(role, content)` | Προσθέτει μήνυμα + validation + trimming | ~3-5 |
| `get_messages()` | Επιστρέφει ιστορικό σε format OpenAI API | ~5-8 |
| `clear()` | Καθαρίζει ιστορικό (κρατάει system prompt!) | ~1 |
| `get_summary()` | Στατιστικά (πλήθος μηνυμάτων ανά ρόλο) | ~5-7 |
| `export_conversation()` | **Bonus**: Εξαγωγή συνομιλίας σε JSON | ~5-8 |

### Δοκιμή

```bash
python conversation_manager.py
```

Θα τρέξουν **7 αυτόματα tests** (6 βασικά + 1 bonus). Αν δείτε `🎉 Τα βασικά tests πέρασαν!`, προχωρήστε στο Βήμα 2.

### Συμβουλές
- Η `add_message()` πρέπει να δέχεται **μόνο** `"user"` ή `"assistant"` ως role — αλλιώς `raise ValueError`
- Η `get_messages()` πρέπει να βάζει πρώτα το system prompt (αν υπάρχει) και μετά τα μηνύματα
- Η `clear()` πρέπει να **κρατάει** το system prompt — μόνο τα μηνύματα αδειάζουν

---

## Βήμα 2: Chatbot — `chatbot.py`

### 🟡 Δυσκολία: Μεσαία | ⏱️ Εκτιμώμενος χρόνος: 20-30 λεπτά

### Θεωρητικό Υπόβαθρο

Το chatbot ακολουθεί αυτή τη ροή:

```
Χρήστης γράφει μήνυμα
        ↓
ConversationManager.add_message("user", message)
        ↓
OpenAI API call (στέλνει ΟΛΟ το ιστορικό)
        ↓
ConversationManager.add_message("assistant", response)
        ↓
Εμφανίζεται η απάντηση
```

### Τι πρέπει να υλοποιήσετε

| Μέθοδος | Τι κάνει | Γραμμές κώδικα |
|---------|----------|:--------------:|
| `chat(user_message)` | Στέλνει μήνυμα στο OpenAI API, αποθηκεύει στο ιστορικό | ~5-6 |
| `switch_personality(name)` | Φορτώνει νέο personality | ~2 |
| `clear_history()` | Καθαρίζει το ιστορικό | ~2 |

### Δοκιμή

```bash
python chatbot.py
python chatbot.py --personality cynical_support
python chatbot.py --list
```

### Συμβουλές

Η μέθοδος `chat()` πρέπει να κάνει τα εξής **με αυτή τη σειρά**:

1. Αποθηκεύει το μήνυμα χρήστη στο ιστορικό
2. Κάνει API call:
   ```python
   response = client.chat.completions.create(
       model="gpt-4o-mini",
       messages=self.conversation.get_messages(),
       max_tokens=500,
       temperature=self.personality.get("temperature", 0.8)
   )
   ```
3. Εξάγει την απάντηση: `response.choices[0].message.content`
4. Αποθηκεύει την απάντηση στο ιστορικό
5. Επιστρέφει την απάντηση

> **Ερώτηση για σκέψη:** Γιατί αποθηκεύουμε ΚΑΙ την απάντηση του assistant στο ιστορικό;

---

## Βήμα 3: Gradio Web UI — `gradio_app.py`

### 🟠 Δυσκολία: Δυσκολότερο | ⏱️ Εκτιμώμενος χρόνος: 25-35 λεπτά

### Θεωρητικό Υπόβαθρο

Το [Gradio](https://www.gradio.app/) είναι μια βιβλιοθήκη Python που δημιουργεί
web interfaces χωρίς HTML/CSS/JS. Βασικά components:

| Component | Τι κάνει |
|-----------|----------|
| `gr.Blocks()` | Container για όλο το UI |
| `gr.Chatbot()` | Εμφάνιση συνομιλίας |
| `gr.Textbox()` | Πεδίο εισαγωγής κειμένου |
| `gr.Dropdown()` | Λίστα επιλογών |
| `gr.Button()` | Κουμπί |

Τα events συνδέουν τα components:
```python
button.click(fn=function, inputs=[input1, input2], outputs=[output1])
```

### Τι πρέπει να υλοποιήσετε

| Συνάρτηση | Τι κάνει |
|-----------|----------|
| `chat(message, history, personality)` | API call στο OpenAI με ιστορικό |
| `respond(message, history, personality)` | Handler: καλεί chat() και ενημερώνει UI |
| `show_greeting(personality, history)` | Εμφανίζει greeting κατά αλλαγή personality |

Αφού υλοποιήσετε τις συναρτήσεις, **αφαιρέστε τα σχόλια `#`** από τα event bindings.

### Δοκιμή

```bash
python gradio_app.py
# → Ανοίξτε http://localhost:7860
```

### Συμβουλές
- Η `chat()` είναι πολύ παρόμοια με αυτή στο Βήμα 2 — η βασική διαφορά είναι ότι εδώ το `history` έρχεται ως argument (λίστα από dicts)
- Η `respond()` πρέπει να επιστρέφει **δύο τιμές**: `("", history)` — κενό textbox + ενημερωμένο ιστορικό
- Η `show_greeting()`: αν το history είναι κενό, δημιουργήστε αρχικό greeting

---

## Βήμα 4: Δημιουργία Personalities — `personalities/*.json`

### 🟢 Δυσκολία: Δημιουργική | ⏱️ Εκτιμώμενος χρόνος: 15-20 λεπτά

### Τι πρέπει να κάνετε

Συμπληρώστε τα `TODO` στα αρχεία:
- `personalities/pirate_expert.json` — Πειρατής-προγραμματιστής
- `personalities/zen_master.json` — Σοφός zen δάσκαλος

### Δομή JSON

Μελετήστε το **δοσμένο παράδειγμα** `cynical_support.json`:

```json
{
    "name": "Όνομα χαρακτήρα",
    "description": "Σύντομη περιγραφή (1-2 προτάσεις)",
    "system_prompt": "Αναλυτικές οδηγίες για τη συμπεριφορά...",
    "temperature": 0.8,
    "greeting": "Αρχικός χαιρετισμός"
}
```

### Οδηγίες για καλό System Prompt

Ένα αποτελεσματικό personality prompt πρέπει να περιέχει:

1. **Ρόλο**: Ποιος/τι είναι ο χαρακτήρας
2. **Στυλ ομιλίας**: Πώς μιλάει (λεξιλόγιο, ύφος, μεταφορές)
3. **Κανόνες συμπεριφοράς**: Τι κάνει και τι αποφεύγει
4. **Παραδείγματα**: 2-3 χαρακτηριστικές φράσεις
5. **Τεχνική ακρίβεια**: Υπενθύμιση ότι οι πληροφορίες πρέπει να είναι σωστές

### Temperature Guide

| Τιμή | Συμπεριφορά | Κατάλληλο για |
|:----:|-------------|---------------|
| 0.0-0.3 | Πολύ ακριβές, ντετερμινιστικό | Factual, τεχνικές απαντήσεις |
| 0.5-0.7 | Ισορροπημένο | Γενικές απαντήσεις |
| 0.8-1.0 | Δημιουργικό, ποικίλο | Ρόλοι με προσωπικότητα |

> **Bonus**: Δημιουργήστε ένα δικό σας personality JSON αρχείο με πρωτότυπο χαρακτήρα!

---

## Βήμα 5: Πειράματα Σύγκρισης — `compare_personalities.py`

### 🔬 Δυσκολία: Παρατήρηση | ⏱️ Εκτιμώμενος χρόνος: 10-15 λεπτά

Αυτό το βήμα είναι **ΔΟΣΜΕΝΟ** — δεν χρειάζεται να γράψετε κώδικα.
Απλά **τρέξτε** και **παρατηρήστε** τα αποτελέσματα.

```bash
python compare_personalities.py
```

### Πείραμα 1: Σύγκριση Personalities

Στέλνει **το ίδιο ερώτημα** ("Explain what a Python decorator is") σε κάθε personality.
Παρατηρήστε πώς η **ίδια ερώτηση** παράγει **εντελώς διαφορετικές** απαντήσεις — αυτή είναι η δύναμη του system prompt.

### Πείραμα 2: Temperature Experiment

Στέλνει **το ίδιο ερώτημα** 3 φορές, με temperatures: `0.0`, `0.5`, `1.0`.

| Temperature | Τι παρατηρείτε |
|:-----------:|----------------|
| **0.0** | Οι 3 απαντήσεις είναι (σχεδόν) **ίδιες** |
| **0.5** | Μικρές διαφοροποιήσεις |
| **1.0** | Κάθε απάντηση είναι **διαφορετική** |

> 📝 Μετά την εκτέλεση, γράψτε τα συμπεράσματά σας σε 2-3 προτάσεις.

---

## Bonus: Export Conversation — `conversation_manager.py`

### ⭐ Δυσκολία: Εύκολο | Προαιρετικό

Στο `conversation_manager.py` υπάρχει μια **bonus μέθοδος** `export_conversation()`
που εξάγει ολόκληρη τη συνομιλία σε μορφή JSON.

- Αν δεν δώσετε filepath → επιστρέφει λίστα dicts
- Αν δώσετε filepath → αποθηκεύει σε αρχείο `.json`

Το Test 7 ελέγχει αυτή τη μέθοδο. Αν δεν την υλοποιήσετε, απλά κάνει skip.

---

## Κριτήρια Αξιολόγησης

| Κριτήριο | Βαρύτητα |
|----------|:--------:|
| Βήμα 1: ConversationManager (περνάει τα 6+1 tests) | 20% |
| Βήμα 2: Λειτουργικό chat (API call + ιστορικό) | 20% |
| Βήμα 3: Λειτουργικό Gradio UI | 20% |
| Βήμα 4: Πρωτότυπα, λειτουργικά personalities | 15% |
| Βήμα 5: Εκτέλεση πειραμάτων + γραπτά συμπεράσματα | 15% |
| Καθαρός κώδικας + σχόλια | 10% |

---

## Ερωτήσεις για Περαιτέρω Σκέψη

1. **Γιατί** στέλνουμε ολόκληρο το ιστορικό σε κάθε API call; Δεν θα ήταν πιο αποδοτικό να στέλνουμε μόνο το τελευταίο μήνυμα;

2. **Τι πρόβλημα** δημιουργεί ένα πολύ μεγάλο ιστορικό; (Hint: context window, κόστος)

3. **Γιατί** χρησιμοποιούμε `max_history=50` στον ConversationManager;

4. Αν αλλάξετε personality με `/switch`, **τι θα γίνει** αν στείλετε μήνυμα; Θα "θυμάται" τα προηγούμενα;

5. Στο Πείραμα 2, **γιατί** με `temperature=0.0` οι απαντήσεις είναι σχεδόν ίδιες; Τι σημαίνει αυτό για τη λειτουργία του token sampling;
