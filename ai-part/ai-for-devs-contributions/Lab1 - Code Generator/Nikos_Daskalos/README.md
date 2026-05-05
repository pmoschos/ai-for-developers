# 🐍 Εργαστηριακή Άσκηση: Code Generator

## Περιγραφή Άσκησης

Σε αυτή την άσκηση θα υλοποιήσετε ένα **εργαλείο γραμμής εντολών (CLI)** που δημιουργεί
Python κώδικα από **φυσική γλώσσα**. Θα εξασκηθείτε στο **prompt engineering** — τη
σωστή διατύπωση οδηγιών ώστε ένα LLM να παράγει ακριβή αποτελέσματα.

Θα δουλέψετε σε **4 βήματα** (αυξανόμενης δυσκολίας).

---

## Στόχοι Μάθησης

| Θέμα | Τι θα μάθετε |
|------|-------------|
| **PCTF Framework** | Πώς δομούμε prompts: Persona, Context, Task, Format |
| **Temperature** | Γιατί χρησιμοποιούμε χαμηλή temperature (0.2) για code generation |
| **Output Parsing** | Πώς καθαρίζουμε την έξοδο ενός LLM (αφαίρεση markdown blocks) |
| **Prompt Chaining** | Πώς χρησιμοποιούμε την έξοδο ενός prompt ως είσοδο σε ένα δεύτερο |
| **CLI Design** | Πώς φτιάχνουμε εργαλεία γραμμής εντολών με `argparse` |

---

## Προαπαιτούμενα

- Python 3.10+
- Βιβλιοθήκες: `openai`, `python-dotenv`
- Αρχείο `.env` στον γονικό φάκελο με:
  ```
  OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
  ```

---

## Δομή Αρχείων

```
code_generator_exe/
├── README.md              ← Αυτό το αρχείο (εκφώνηση)
├── prompts.py             ← Βήμα 1: Prompt templates
├── code_gen.py            ← Βήμα 2: Βασική code generation
├── code_generator.py      ← Βήμα 3: CLI με argparse
└── examples.md            ← ΔΟΣΜΕΝΟ: Παραδείγματα χρήσης
```

> **Σημείωση:** Τα αρχεία που θα επεξεργαστείτε περιέχουν σχόλια `TODO` στα σημεία
> που χρειάζεται κώδικας. Τα τμήματα με σχόλιο `ΔΟΣΜΕΝΟ` δεν χρειάζονται αλλαγή.

---

## Βήμα 1: Prompt Templates — `prompts.py`

### 🟢 Δυσκολία: Εύκολο | ⏱️ Εκτιμώμενος χρόνος: 15-20 λεπτά

### Θεωρητικό Υπόβαθρο — PCTF Framework

Ένα καλό prompt ακολουθεί τη δομή **PCTF**:

| Στοιχείο | Τι κάνει | Παράδειγμα |
|----------|----------|-----------|
| **P**ersona | Ρόλος του AI | "You are an expert Python developer" |
| **C**ontext | Πλαίσιο | "You are helping developers generate code" |
| **T**ask | Τι ζητάμε | "Generate a Python function based on..." |
| **F**ormat | Μορφή εξόδου | "Return ONLY the Python code" |

### Τι πρέπει να υλοποιήσετε

| Prompt | Τι κάνει |
|--------|----------|
| `CODE_GENERATION_PROMPT` | Δημιουργεί Python function από περιγραφή |
| `TEST_GENERATION_PROMPT` | Δημιουργεί pytest tests για δεδομένο κώδικα |

### Συμβουλές
- Το placeholder `{description}` θα αντικατασταθεί αυτόματα με `.format()`
- Η μορφή εξόδου (Format) είναι **κρίσιμη** — αν δεν πείτε "no markdown", θα πάρετε ` ```python ` blocks
- Ένα **αναλυτικό** prompt δίνει **καλύτερα** αποτελέσματα

### Δοκιμή

```bash
python prompts.py
```

Θα εμφανιστούν τα prompts σας για οπτικό έλεγχο.

---

## Βήμα 2: Βασική Code Generation — `code_gen.py`

### 🟡 Δυσκολία: Μεσαία | ⏱️ Εκτιμώμενος χρόνος: 20-30 λεπτά

### Θεωρητικό Υπόβαθρο

Η ροή δημιουργίας κώδικα:

```
Περιγραφή (φυσική γλώσσα)
        ↓
Prompt template + .format(description=...)
        ↓
OpenAI API call (temperature=0.2 → λίγη δημιουργικότητα)
        ↓
Καθαρισμός εξόδου (αφαίρεση ``` markdown)
        ↓
Κώδικας Python
```

Το **Prompt Chaining** χρησιμοποιείται για τα tests:
```
Βήμα 1: description → Κώδικας
Βήμα 2: Κώδικας   → Tests (ο κώδικας γίνεται input!)
```

### Τι πρέπει να υλοποιήσετε

| Συνάρτηση | Τι κάνει | Γραμμές |
|-----------|----------|:-------:|
| `generate_code()` | API call + prompt formatting + prompt chaining | ~15-20 |
| `clean_code_output()` | Αφαίρεση ` ```python ``` ` markers | ~5-8 |
| `save_code()` | Αποθήκευση σε αρχείο | ~5-7 |

### Δοκιμή

```bash
python code_gen.py
```

Θα κληθούν 3 παραδείγματα αυτόματα.

### Συμβουλές
- **temperature=0.2**: Για κώδικα θέλουμε **ακρίβεια**, όχι δημιουργικότητα
- Η `clean_code_output()` πρέπει να χειρίζεται ΚΑΙ ` ```python` ΚΑΙ ` ``` ` (χωρίς γλώσσα)
- Στο prompt chaining, ο κώδικας που παράγεται στο Βήμα 1 μπαίνει στο `TEST_GENERATION_PROMPT`

> **Ερώτηση για σκέψη:** Γιατί δεν ζητάμε κώδικα ΚΑΙ tests σε ένα μόνο prompt;

---

## Βήμα 3: CLI με argparse — `code_generator.py`

### 🟠 Δυσκολία: Δυσκολότερο | ⏱️ Εκτιμώμενος χρόνος: 20-30 λεπτά

### Θεωρητικό Υπόβαθρο

Ένα CLI tool πρέπει να δέχεται arguments:
```bash
python code_generator.py "description" --with-tests --save output.py
```

Η βιβλιοθήκη `argparse` χειρίζεται:
- **Positional arguments**: `description`
- **Optional flags**: `--with-tests`, `--save FILE`
- **Help**: `python code_generator.py --help`

### Τι πρέπει να υλοποιήσετε

| Συνάρτηση / Τμήμα | Τι κάνει |
|-----------|----------|
| `generate_code()` | Ίδια λογική με Βήμα 2, χωρίς display |
| `interactive_mode()` | Βρόχος που ρωτάει τον χρήστη |
| `main()` | argparse setup + κλήση κατάλληλης λειτουργίας |

### Δοκιμή

```bash
# Ένα απλό generation
python code_generator.py "a function that reverses a string"

# Με tests
python code_generator.py "binary search" --with-tests

# Αποθήκευση σε αρχείο
python code_generator.py "factorial" --save factorial.py

# Interactive mode
python code_generator.py -i
```

### Συμβουλές
- Η `interactive_mode()` ακολουθεί pattern: input → generate → display → save? → repeat
- Η `main()` πρέπει να ελέγχει: αν δεν δόθηκε description ΚΑΙ δεν είναι interactive → τρέξε interactive

---

## Βήμα 4: Πείραμα Prompt Engineering

### 🔬 Δυσκολία: Παρατήρηση | ⏱️ Εκτιμώμενος χρόνος: 10-15 λεπτά

Αφού ολοκληρώσετε τα Βήματα 1-3, δοκιμάστε τα εξής:

### 4a. Σύγκριση Prompt Quality

Τρέξτε generation με **ασαφή** vs **συγκεκριμένη** περιγραφή:

```bash
# Ασαφές
python code_generator.py "a sort function"

# Συγκεκριμένο
python code_generator.py "a function that implements quicksort with in-place partitioning for a list of integers"
```

> 📝 Καταγράψτε τις διαφορές στην ποιότητα κώδικα.

### 4b. Temperature Experiment

Στο `code_gen.py`, δοκιμάστε να αλλάξετε `temperature=0.2` σε `temperature=0.9`
και τρέξτε ξανά. Συγκρίνετε τα αποτελέσματα.

> 📝 Γράψτε τα συμπεράσματά σας σε 2-3 προτάσεις.

---

## Κριτήρια Αξιολόγησης

| Κριτήριο | Βαρύτητα |
|----------|:--------:|
| Βήμα 1: Σωστά PCTF prompts (παράγουν λειτουργικό κώδικα) | 25% |
| Βήμα 2: Λειτουργική code generation + clean output + save | 25% |
| Βήμα 3: Πλήρες CLI (argparse + interactive mode) | 25% |
| Βήμα 4: Πειράματα + γραπτά συμπεράσματα | 15% |
| Καθαρός κώδικας + σχόλια | 10% |

---

## Ερωτήσεις για Περαιτέρω Σκέψη

1. **Γιατί** χρησιμοποιούμε `temperature=0.2` για code generation αλλά `0.8` για chatbot;

2. **Γιατί** λέμε "Return ONLY the Python code, no markdown" στο prompt; Τι γίνεται χωρίς αυτή την οδηγία;

3. **Τι είναι** το Prompt Chaining και γιατί δεν ζητάμε κώδικα + tests μαζί;

4. Η `clean_code_output()` είναι "hack" ή best practice; **Πώς** θα μπορούσαμε να αποφύγουμε εντελώς τα markdown blocks;

5. **Τι θα γινόταν** αν αφαιρούσαμε τo Persona section από το prompt;
