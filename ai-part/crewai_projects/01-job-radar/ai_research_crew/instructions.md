# AiResearchCrew / JobRadar

Αυτό το αρχείο περιγράφει πώς να στήσεις, να τρέξεις και να κατανοήσεις το
project `ai_research_crew` από το μηδέν. Είναι γραμμένο για έναν φοιτητή
πληροφορικής που ξέρει Python και έχει βασικές γνώσεις GenAI.

Το project είναι μία CrewAI εφαρμογή που:
- βρίσκει πραγματικές θέσεις εργασίας
- αναλύει τις απαιτήσεις της αγοράς
- συγκρίνει το CV με την αγορά
- παράγει σκορ ετοιμότητας και roadmap 90 ημερών
- δείχνει τα αποτελέσματα σε Gradio UI

---

## Περιεχόμενα

1. Εισαγωγή: τι είναι αυτό το project
2. Απαιτούμενα
3. Δομή αρχείων
4. Πώς δουλεύει το pipeline
5. Βήμα-βήμα setup
6. `.env` και κλειδιά
7. Εκτέλεση CLI
8. Εκτέλεση Gradio UI
9. Debugging / κοινά προβλήματα
10. Πώς να φτιάξεις το ίδιο project από την αρχή
11. Χρήσιμες εντολές

---

## 1) Τι είναι αυτό το project

Το project είναι ένα multi-agent CrewAI pipeline με:
- `JobHunter` agent για web search
- `MarketAnalyst` για data-driven ανάλυση δεξιοτήτων
- `GapAdvisor` για σύγκριση CV με την αγορά
- `RoadmapWriter` για 90-day learning plan
- `Director` που ορίζει την ποιότητα και συντονίζει την ιεραρχική ροή

Η εφαρμογή τρέχει από το CLI και από ένα Gradio dashboard.

---

## 2) Απαιτούμενα

- Python 3.10 / 3.11 / 3.12
- Git (προαιρετικά)
- OpenAI API key
- Tavily API key
- Virtual environment (`venv`)
- Πακέτα Python: `crewai[tools]`, `openai`, `gradio`, `python-dotenv`, `tavily-python`

---

## 3) Δομή αρχείων

Το project έχει αυτή τη δομή:

- `pyproject.toml` — dependencies + crew type
- `.env.example` — παράδειγμα env vars
- `app.py` — Gradio UI και το pipeline stream runner
- `src/ai_research_crew/`:
  - `__init__.py`
  - `crew.py` — ο κύριος CrewAI ορισμός
  - `main.py` — CLI entry point
  - `models.py` — Pydantic μοντέλα για την έξοδο
  - `config/agents.yaml` — ρυθμίσεις agents
  - `config/tasks.yaml` — ρυθμίσεις tasks
  - `tools/fetch_tool.py` — εργαλείο για web page fetch
  - `tools/notify_tool.py` — εργαλείο για αποστολή ειδοποιήσεων
  - `tools/custom_tool.py` — παράδειγμα custom tool
- `output/` — εκτυπωμένα αποτελέσματα
- `memory/` — CrewAI memory store

---

## 4) Πώς δουλεύει το pipeline

### `crew.py`

Το file ορίζει την κλάση `JobRadar` με:
- `@CrewBase`
- `@agent` methods για κάθε agent
- `@task` methods για κάθε task
- `@crew` method που επιστρέφει το `Crew()` object

Η εκτέλεση είναι hierarchical:
- Ο `director` agent επιβλέπει και συντονίζει
- Οι 4 σταδιακοί agents εκτελούν τα tasks
- Ο `Crew` μπορεί να ενημερώσει, να ζητήσει rewrite, και να διαχειριστεί ποιότητα

### Τα 4 στάδια

1. `hunt_task` → `job_hunter` → `JobListings`
2. `analyse_task` → `market_analyst` → `MarketAnalysis`
3. `gap_task` → `gap_advisor` → `GapAnalysis`
4. `roadmap_task` → `roadmap_writer` → Markdown roadmap

### `models.py`

Τα Pydantic μοντέλα είναι οι συμβάσεις μεταξύ των σταδίων.
Αν ο agent δεν επιστρέψει έγκυρο JSON, το CrewAI θα ζητήσει διόρθωση.

Σημαντικό:
- Το `readiness_score` υπολογίζεται ως:
  `(matched critical skills / total critical skills) * 100`
- Αν το score βγει 0, σημαίνει ότι το CV δεν καλύπτει κανένα απαραίτητο skill

### `agents.yaml` και `tasks.yaml`

Το `agents.yaml` ορίζει:
- role
- goal
- backstory
- llm

Το `tasks.yaml` ορίζει:
- description
- expected_output
- agent
- context
- output_file

Το `context` μεταφέρει τα αποτελέσματα από τα προηγούμενα tasks.

### `app.py`

Το Gradio UI:
- δημιουργεί input fields
- τρέχει το `run_analysis()` σε background thread
- κάνει streaming logs σε πραγματικό χρόνο
- διαβάζει το `output/03_gap_analysis.json` και `output/04_learning_roadmap.md`

---

## 5) Βήμα-βήμα setup

### 5.1) Δημιουργία project folder

```powershell
mkdir ai_research_crew
cd ai_research_crew
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
mkdir ai_research_crew
cd ai_research_crew
python3 -m venv .venv
source .venv/bin/activate
```

### 5.2) Εγκατάσταση dependencies

```bash
pip install --upgrade pip
pip install crewai[tools]==1.14.4 openai gradio python-dotenv tavily-python
```

Αν θες `uv`:

```bash
uv tool install crewai
uv add "crewai[tools]==1.14.4" openai gradio python-dotenv tavily-python
```

### 5.3) Βεβαίωση εγκατάστασης

```bash
python -c "import openai, gradio, dotenv, tavily; print('ok')"
```

---

## 6) `.env` και κλειδιά

Το `.env` πρέπει να περιέχει τουλάχιστον:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=...
```

Προαιρετικά, αν θέλεις notifications:

```env
NTFY_TOPIC=jobradar-alerts
NTFY_TOKEN=
RESEND_API_KEY=...
REPORT_FROM=you@example.com
REPORT_TO=recipient@example.com
```

Σημείωση:
- Το `.env.example` περιέχει παλαιότερα κλειδιά (`SERPER_API_KEY`,
  `SENDGRID_API_KEY`) αλλά το project χρησιμοποιεί `TAVILY_API_KEY`.
- Το βασικό `.env` του project πρέπει να περιέχει `OPENAI_API_KEY` και
  `TAVILY_API_KEY` για να τρέξει το CLI.

---

## 7) Εκτέλεση CLI

Το CLI entry point είναι το `src/ai_research_crew/main.py`.

Τρέξε:

```bash
python -m ai_research_crew.main
```

ή με `uv`:

```bash
uv run python -m ai_research_crew.main
```

Το script θα:
- επαληθεύσει env vars
- ζητήσει Job Title, Location, CV
- τρέξει `JobRadar().crew().kickoff(inputs=...)`
- γράψει αρχεία στο `output/`

Αποτελέσματα:
- `output/01_job_listings.json`
- `output/02_market_analysis.json`
- `output/03_gap_analysis.json`
- `output/04_learning_roadmap.md`

---

## 8) Εκτέλεση Gradio UI

Τρέξε:

```bash
python app.py
```

Ανοίγει browser UI με:
- Live agent log
- Readiness score card
- 90-day roadmap preview
- επιλογή output αρχείων

Το `run_analysis()`:
- τρέχει το CrewAI pipeline σε ξεχωριστό thread
- captures stdout logs
- ανανεώνει το UI μέχρι να ολοκληρωθεί

---

## 9) Debugging / κοινά προβλήματα

### Πρόβλημα 1: Missing env vars

Το `main.py` σταματάει αν λείπουν:
- `OPENAI_API_KEY`
- `TAVILY_API_KEY`

### Πρόβλημα 2: 403 embedding permissions

Η ρύθμιση στο `crew.py` είναι:

```python
embedder={
    "provider": "openai",
    "config": {"model_name": "text-embedding-3-large"},
},
```

Αν το API key σου δεν έχει πρόσβαση, δοκίμασε:
- να αλλάξεις model σε επιτρεπτό embed model
- να θέσεις `memory=False` προσωρινά για debugging

### Πρόβλημα 3: `readiness_score` = 0

Αυτό σημαίνει ότι το CV δεν περιέχει κανένα από τα critical skills που
εντόπισε ο `Market Analyst`.
Έλεγξε το `output/03_gap_analysis.json`.

### Πρόβλημα 4: Gradio UI δεν φορτώνει αρχεία

Το UI φορτώνει τα `output/*.json` και `output/*.md`. Αν προσθέσεις new files
ενώ το app τρέχει, επανεκκίνησέ το.

### Πρόβλημα 5: ModuleNotFoundError

Βεβαιώσου ότι είσαι στο σωστό interpreter του `.venv` και ότι έχεις
εγκαταστήσει τα packages εκεί.

---

## 10) Πώς να φτιάξεις το ίδιο project από την αρχή

Αν θέλεις να δημιουργήσεις το ίδιο project από μηδέν, ακολούθησε αυτά τα βήματα:

1. Φτιάξε τη δομή των φακέλων:
   - `src/ai_research_crew/`
   - `src/ai_research_crew/config/`
   - `src/ai_research_crew/tools/`
   - `output/`
   - `memory/`

2. Δημιούργησε τα αρχεία:
   - `pyproject.toml`
   - `.env.example`
   - `app.py`
   - `src/ai_research_crew/__init__.py`
   - `src/ai_research_crew/crew.py`
   - `src/ai_research_crew/main.py`
   - `src/ai_research_crew/models.py`
   - `src/ai_research_crew/config/agents.yaml`
   - `src/ai_research_crew/config/tasks.yaml`
   - `src/ai_research_crew/tools/fetch_tool.py`
   - `src/ai_research_crew/tools/notify_tool.py`

3. Στο `pyproject.toml` βάλε:

```toml
[project]
name = "ai_research_crew"
version = "0.1.0"
requires-python = ">=3.10,<3.14"
dependencies = [
    "crewai[tools]==1.14.4",
    "gradio>=6.14.0",
    "openai>=2.38.0",
    "python-dotenv>=1.2.2",
    "requests>=2.34.2",
    "resend>=2.30.1",
    "sendgrid>=6.12.5",
    "tavily-python>=0.7.24",
]

[tool.crewai]
type = "crew"
```

4. Στο `crew.py` χρησιμοποίησε το `@CrewBase` και φτιάξε:
   - 4 agents με `@agent`
   - 4 tasks με `@task`
   - `@crew` που επιστρέφει `Crew(...)`

5. Στο `models.py` ορίστε τα Pydantic models:
   - `JobListing`, `JobListings`
   - `SkillDemand`, `MarketAnalysis`
   - `GapAnalysis`

6. Στο `agents.yaml` γράψε role/goal/backstory/llm όπως στο project.

7. Στο `tasks.yaml` γράψε description/expected_output/agent/context/output_file.

8. Στο `app.py` υλοποίησε Gradio UI που:
   - ζητά input
   - τρέχει `JobRadar().crew().kickoff(...)`
   - εμφανίζει logs και αρχεία `output/`

9. Πρόσθεσε τα εργαλεία:
   - `WebFetchTool` για fetch URL
   - `NotificationTool` για ntfy.sh + Resend email

---

## 11) Χρήσιμες εντολές

```bash
# Ενεργοποίηση venv (Windows)
& .\.venv\Scripts\Activate.ps1

# Ενεργοποίηση venv (macOS/Linux)
source .venv/bin/activate

# Εκτέλεση CLI
python -m ai_research_crew.main

# Εκτέλεση Gradio UI
python app.py

# Έλεγχος output
ls output
cat output/03_gap_analysis.json

# Γρήγορη δοκιμή import
python -c "import sys; sys.path.insert(0,'src'); from ai_research_crew.crew import JobRadar; print(JobRadar().crew())"
```
