# 🚀 Οδηγίες Εγκατάστασης & Εκτέλεσης

## Προαπαιτούμενα

- **Python ≥ 3.11** (ελέγξτε με `python --version`)
- **OpenAI API key**
- **Tavily API key**

---

## Βήμα 1 — Δημιουργία Virtual Environment

```powershell
python -m venv .venv
```

Δημιουργεί τον φάκελο `.venv` με ένα απομονωμένο περιβάλλον Python.

---

## Βήμα 2 — Ενεργοποίηση Virtual Environment

**Windows (PowerShell):**

```powershell
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

> Θα δείτε `(.venv)` στην αρχή του prompt — αυτό σημαίνει ότι είναι ενεργό.

---

## Βήμα 3 — Εγκατάσταση Dependencies

```powershell
pip install -e ".[dev]"
```

### Τι κάνει αυτή η εντολή;

| Κομμάτι   | Σημασία                                                                 |
|-----------|-------------------------------------------------------------------------|
| `pip install` | Εγκατάσταση πακέτου                                                 |
| `-e`      | **Editable mode** — ο κώδικας τρέχει απευθείας από το `src/`, χωρίς αντιγραφή. Κάθε αλλαγή εφαρμόζεται αμέσως. |
| `.`       | Ο τρέχων φάκελος — διαβάζει το `pyproject.toml`                        |
| `[dev]`   | Εγκαθιστά και τα dev dependencies (pytest, pytest-cov)                  |

### Τι εγκαθίσταται:

**Βασικά dependencies:**

- `gradio` — interactive web UI
- `langgraph` — unified stateful graph με `interrupt()` + `MemorySaver`
- `langchain` + `langchain-openai` — LLM integration με structured output
- `langchain-tavily` — web search
- `pydantic` — structured LLM output (ProposalOutput model)
- `pydantic-settings` — type-validated configuration (BaseSettings)
- `tenacity` — retry logic με exponential backoff
- `python-dotenv` — environment variables

**Dev dependencies (μόνο με `[dev]`):**

- `pytest` — testing framework
- `pytest-cov` — code coverage

---

## Βήμα 4 — Ρύθμιση API Keys

Αντιγράψτε το template:

```powershell
copy .env.example .env
```

Επεξεργαστείτε το `.env` και βάλτε τα πραγματικά κλειδιά σας:

```env
OPENAI_API_KEY=sk-your-real-openai-key
TAVILY_API_KEY=tvly-your-real-tavily-key
```

### Προαιρετικές ρυθμίσεις στο `.env`

| Μεταβλητή | Default | Περιγραφή |
|-----------|---------|-----------|
| `LLM_MODEL` | `gpt-4o-mini` | Μοντέλο OpenAI |
| `LLM_TEMPERATURE` | `0.0` | Θερμοκρασία LLM |
| `TAVILY_MAX_RESULTS` | `5` | Μέγιστα αποτελέσματα αναζήτησης |
| `SERVER_HOST` | `127.0.0.1` | Gradio server host |
| `SERVER_PORT` | `7860` | Gradio server port |
| `LOG_LEVEL` | `INFO` | Επίπεδο logging (DEBUG, INFO, WARNING, ERROR) |

Η ρύθμιση γίνεται μέσω `pydantic-settings` — όλες οι μεταβλητές ελέγχονται και επικυρώνονται κατά την εκκίνηση.

---

## Βήμα 5 — Εκτέλεση

```powershell
python -m hitl_search_agent
```

Η εφαρμογή ξεκινά στο **http://127.0.0.1:7860** 🎉

### Πώς λειτουργεί η εντολή `python -m`;

Η αλυσίδα εκτέλεσης:

```
python -m hitl_search_agent
        │
        ▼
   __main__.py          ← η Python ψάχνει αυτό το αρχείο αυτόματα
        │
        │   from hitl_search_agent.main import main
        │   main()
        ▼
     main.py            ← ρυθμίζει logging, φορτώνει settings, χτίζει UI
        │
        │   setup_logging(level=settings.log_level)
        │   demo = build_ui()
        │   demo.launch(server_name=..., server_port=...)
        ▼
   http://127.0.0.1:7860
```

1. Το `-m` σημαίνει **"τρέξε αυτό σαν module"**. Η Python ψάχνει αυτόματα ένα αρχείο `__main__.py` μέσα στο πακέτο `hitl_search_agent`.
2. Το `__main__.py` καλεί τη `main()` από το `main.py`.
3. Η `main()`:
   - Φορτώνει τις ρυθμίσεις μέσω `pydantic-settings`
   - Ρυθμίζει το structured logging
   - Χτίζει το Gradio UI (`build_ui()`)
   - Ξεκινά τον server (`demo.launch()`)

**Γιατί λειτουργεί μετά το `pip install -e .`;**

Το `pip install -e .` διαβάζει αυτό στο `pyproject.toml`:

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

Αυτό κάνει register το `src/hitl_search_agent` στην Python, ώστε η εντολή `python -m hitl_search_agent` να βρει το πακέτο σε **οποιοδήποτε directory** κι αν βρίσκεστε — όχι μόνο μέσα στο `src/`.

---

## Εκτέλεση Tests

```powershell
# Όλα τα tests (31 tests)
pytest -v

# Με code coverage
pytest -v --cov=hitl_search_agent --cov-report=term-missing

# Μόνο integration tests (full interrupt/resume cycle)
pytest tests/test_integration.py -v
```

### Τι καλύπτουν τα tests:

| Test File | Τι ελέγχει |
|-----------|-----------|
| `test_config.py` | Φόρτωση ρυθμίσεων, defaults, validation |
| `test_image_utils.py` | Εξαγωγή εικόνων από Tavily αποτελέσματα |
| `test_integration.py` | Πλήρης ροή: approve, reject, edited query (με interrupt/resume) |
| `test_nodes.py` | Structured output, retry logic, routing |
| `test_workflow.py` | Service layer, thread-ID, custom exceptions |

---

## Πώς λειτουργεί η εφαρμογή

### Αρχιτεκτονική — Ενιαίος Graph με interrupt()

```
START → propose_action → human_review (interrupt)
      → route: approved  → execute_web_search → summarize → END
      → route: rejected  → END
```

### Ροή βήμα-βήμα:

1. Εισάγετε ένα αίτημα αναζήτησης στο Gradio UI
2. Το LLM (`gpt-4o-mini`) παράγει **structured output** (Pydantic `ProposalOutput`) — δεν χρειάζεται JSON parsing
3. Ο graph **διακόπτεται** με `interrupt()` στο `human_review` node
4. **Εσείς αποφασίζετε** — approve, edit, ή reject
5. Ο graph **συνεχίζει** μέσω `Command(resume=...)` με την απόφασή σας
6. Αν εγκρίνετε → Tavily κάνει αναζήτηση (με retry) → LLM συνοψίζει → εμφάνιση αποτελεσμάτων & εικόνων
7. Αν απορρίψετε → ο graph τερματίζει χωρίς αναζήτηση

### Production Features:

- **Checkpointing**: Κάθε συνομιλία έχει δικό της `thread_id` — το state διατηρείται μέσω `MemorySaver`
- **Retry**: Αν το Tavily αποτύχει, ξαναδοκιμάζει έως 3 φορές με exponential backoff
- **Logging**: Structured logging σε κάθε module — βλέπετε τι γίνεται στο terminal

---

## Απενεργοποίηση Virtual Environment

Όταν τελειώσετε:

```powershell
deactivate
```
