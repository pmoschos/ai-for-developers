# 🚀 Οδηγίες Εκκίνησης — LangChain + LangSmith Edition

---

## Βήμα 1 — Άνοιξε το Terminal

Άνοιξε **PowerShell** ή **Command Prompt** και πήγαινε στον φάκελο του project:

```bash
cd C:\Users\user\Downloads\module_04_rag_langchain
```

> ✅ Επαλήθευση: τρέξε `dir` — θα πρέπει να βλέπεις `gradio_app.py` στη λίστα.

---

## Βήμα 2 — Δημιούργησε Virtual Environment

```bash
python -m venv venv
```

Αυτό δημιουργεί έναν απομονωμένο χώρο για τα Python packages του project.

> ⏳ Διαρκεί ~10-20 δευτερόλεπτα. Δεν εμφανίζει output αν πάει καλά.

---

## Βήμα 3 — Ενεργοποίησε το Virtual Environment

```bash
venv\Scripts\activate
```

> ✅ Επαλήθευση: το prompt αλλάζει σε `(venv) C:\Users\user\Downloads\module_04_rag_langchain>`

---

## Βήμα 4 — Εγκατέστησε τα Packages

```bash
pip install langchain langchain-community langchain-openai langchain-chroma langchain-text-splitters langsmith chromadb openai gradio python-dotenv pypdf python-docx unstructured
```

> ⏳ Διαρκεί **2-5 λεπτά** ανάλογα με τη σύνδεση.
> Θα δεις πολλές γραμμές `Downloading...` / `Installing...` — αυτό είναι φυσιολογικό.

---

## Βήμα 5 — Έλεγξε το `.env`

Βεβαιώσου ότι το αρχείο `.env` έχει **έγκυρο** OpenAI API key:

```
OPENAI_API_KEY="sk-proj-..."
```

> **Προαιρετικό — LangSmith tracing:**
> Αν έχεις λογαριασμό στο [smith.langchain.com](https://smith.langchain.com), πρόσθεσε:
> ```
> LANGCHAIN_TRACING_V2=true
> LANGCHAIN_API_KEY="ls__..."
> LANGCHAIN_PROJECT="module-04-rag"
> ```
> Από εκεί και πέρα **κάθε** LangChain call εμφανίζεται αυτόματα στο LangSmith dashboard
> με latency, tokens, κόστος, και retrieved documents.

---

## Βήμα 6 — Εκκίνησε την Εφαρμογή

```bash
python gradio_app.py
```

> ✅ Επιτυχία — θα δεις:
> ```
> Running on local URL: http://127.0.0.1:7860
> ```

Άνοιξε τον browser και πήγαινε στη διεύθυνση:
**[http://127.0.0.1:7860](http://127.0.0.1:7860)**

---

## Βήμα 7 — Πρώτη Χρήση

1. Πήγαινε στο tab **📁 Upload Documents**
2. Ανέβασε ένα αρχείο (PDF, TXT, MD, DOCX)
3. Πάτα **⬆️ Ingest Document** — περίμενε μήνυμα `✅ X chunks added`
4. Πήγαινε στο tab **💬 Chat**
5. Ρώτα κάτι σχετικό με το έγγραφο!

---

## 🔄 Επόμενες Φορές

Δεν χρειάζεται να ξανακάνεις τα Βήματα 2 και 4. Μόνο:

```bash
cd C:\Users\user\Downloads\module_04_rag_langchain
venv\Scripts\activate
python gradio_app.py
```

---

## ❗ Συχνά Προβλήματα

| Πρόβλημα | Λύση |
|----------|------|
| `ModuleNotFoundError` | Βεβαιώσου ότι το venv είναι ενεργό (`venv\Scripts\activate`) |
| `AuthenticationError` | Ο OpenAI API key δεν είναι έγκυρος — έλεγξε το `.env` |
| `port already in use` | Κλείσε ό,τι τρέχει στην πόρτα 7860 ή άλλαξε: `app.launch(server_port=7861)` |
| `pip` δεν βρίσκεται | Τρέξε `python -m pip install ...` αντί `pip install ...` |

---

---

# 🗂️ Δομή Project & Αρχεία

```
module_04_rag_langchain/
│
├── .env                                  ← 🔑 API Keys
├── gradio_app.py                         ← 🖥️  Web UI
├── SETUP.md                              ← 📖 Αυτό το αρχείο
├── requirements.txt                      ← 📦 Python dependencies
│
└── document_qa_bot/
    ├── config.py                         ← ⚙️  Παράμετροι συστήματος
    ├── rag_pipeline.py                   ← 🔗 Orchestrator (glue code)
    │
    ├── ingestion/
    │   └── ingestor.py                   ← 📄 Φόρτωση & κατατεμαχισμός
    │
    ├── retrieval/
    │   └── retriever.py                  ← 🔍 Vector search & διαχείριση DB
    │
    └── generation/
        ├── prompts.py                    ← 📝 System prompts / Personas
        └── chain_builder.py             ← 🔗 LCEL chain & streaming
```

---

## Ανάλυση Αρχείων

---

### `.env` — API Keys & Configuration

```
OPENAI_API_KEY="sk-proj-..."          ← Απαραίτητο
LANGCHAIN_TRACING_V2=true             ← Προαιρετικό (LangSmith)
LANGCHAIN_API_KEY="ls__..."           ← Προαιρετικό (LangSmith)
LANGCHAIN_PROJECT="module-04-rag"     ← Προαιρετικό (LangSmith)
```

---

### `gradio_app.py` — Web UI

Ορίζει το **Gradio interface** με 4 tabs:

| Tab | Λειτουργία |
|-----|-----------|
| **💬 Chat** | Ερωτήσεις, HyDE toggle, streaming display, sources, token stats |
| **📁 Upload** | Ανέβασμα και ingestion εγγράφων στο ChromaDB |
| **📊 Stats** | Εμφάνιση αριθμού chunks & πηγών, clear database |
| **⚙️ Settings** | Επιλογή persona μέσω preset buttons ή custom prompt |

Το **Chat tab** έχει:
- **🧪 Use HyDE checkbox** — ενεργοποιεί HyDE retrieval αντί standard
- **💡 HyDE Accordion** — εμφανίζει το hypothetical document που δημιούργησε το LLM
- **Token display** — δείχνει `🧪 HyDE` ή `🔍 Standard` + token count + κόστος

Δεν περιέχει RAG logic — **αποκλειστικά UI code** που καλεί το `RAGPipeline`.

```python
# Singleton — δημιουργείται μία φορά, χρησιμοποιείται παντού
pipeline = RAGPipeline()
pipeline.ingest(file_path)
pipeline.answer_stream(question, history, use_hyde=True)  # ή False
pipeline.get_stats()
```

---

### `document_qa_bot/config.py` — Παράμετροι Συστήματος

Singleton με `@lru_cache()` — διαβάζεται μία φορά και επαναχρησιμοποιείται.

```python
@dataclass
class Config:
    chunk_size: int = 1000          # χαρακτήρες ανά chunk
    chunk_overlap: int = 200        # επικάλυψη μεταξύ chunks
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    temperature: float = 0.3
    chroma_db_path: Path = ...      # τοπικό path για ChromaDB persistence
```

---

### `document_qa_bot/rag_pipeline.py` — Orchestrator

**Glue code** που αρχικοποιεί και συνδέει τα τρία components.
Δεν περιέχει business logic — μόνο delegation.

```python
class RAGPipeline:
    def __init__(self):
        # Δημιουργεί: embeddings, vectorstore, llm
        # Συνδέει: DocumentIngestor, VectorRetriever, ChainBuilder

    def ingest(file_path)                      → DocumentIngestor.ingest()
    def answer_stream(q, history, use_hyde)    → ChainBuilder.answer_stream()
    def get_stats()                            → VectorRetriever.get_stats()
    def clear()                                → VectorRetriever.clear()
    def set_system_prompt(prompt)              → ChainBuilder.build(prompt)
```

---

### `ingestion/ingestor.py` — Φόρτωση & Κατατεμαχισμός

**Single Responsibility:** Load → Split → Store

| Βήμα | LangChain Component | Λεπτομέρειες |
|------|-------------------|-------------|
| Load | `PyPDFLoader`, `TextLoader`, `Docx2txtLoader`, `UnstructuredMarkdownLoader` | Επιλογή loader βάσει extension |
| Split | `RecursiveCharacterTextSplitter` | 1000 χαρ., 200 overlap, separators: `\n\n`, `\n`, `. `, ` ` |
| Store | `vectorstore.add_documents(chunks)` | Αυτόματο embedding + αποθήκευση στο ChromaDB |

```python
class DocumentIngestor:
    def ingest(file_path: str) -> int:   # επιστρέφει αριθμό chunks
    def _load(file_path: str) -> List:   # επιλέγει το σωστό loader
```

---

### `retrieval/retriever.py` — Vector Search & Διαχείριση DB

**Single Responsibility:** Semantic search + stats + management

```python
class VectorRetriever:
    def as_retriever(k=4)   # επιστρέφει LangChain retriever για LCEL chains
    def get_stats() -> Dict # total_chunks, unique_sources, sources list
    def clear()             # διαγραφή όλων + επανάχρηση άδειας collection
```

Χρησιμοποιεί **ChromaDB** με cosine similarity:
- `score = 1 - cosine_distance` → 1.0 = ταυτόσημο, 0.0 = άσχετο

---

### `generation/prompts.py` — System Prompts / Personas

Τέσσερα έτοιμα personas που εμφανίζονται ως preset buttons στο Settings tab:

| Persona | Button | Χρήση |
|---------|--------|-------|
| `QA_SYSTEM_PROMPT` | ↩️ Default | Balanced, accurate, citations |
| `QA_DETAILED_PROMPT` | 🎓 Academic | Αναλυτικές απαντήσεις με [Source N] |
| `QA_CONCISE_PROMPT` | ✂️ Concise | 1-2 προτάσεις μόνο |
| `QA_KIDS_PROMPT` | 👧 Kids Friendly | Παιδική αφήγηση μύθων Αισώπου |
| `CONTEXTUALIZE_PROMPT` | (εσωτερικό) | Reformulation ερωτήσεων βάσει ιστορικού |

---

### `generation/chain_builder.py` — LCEL Chain & Streaming

**Single Responsibility:** Χτίζει την LCEL chain + streaming απαντήσεων

Υποστηρίζει **δύο retrieval modes** που επιλέγονται από το `use_hyde` flag:

---

**🔍 Standard Mode** (`use_hyde=False` — default)

```
Ερώτηση + Ιστορικό
      ↓
get_query()  ← αν υπάρχει ιστορικό, reformulates "she" → "Mira"
      ↓
ChromaDB.similarity_search(question_embedding, k=4)
      ↓
format_docs() → context string
      ↓
QA Prompt (system + context + history + question)
      ↓
ChatOpenAI (streaming=True) → token stream
```

---

**🧪 HyDE Mode** (`use_hyde=True`)

```
Ερώτηση
      ↓
_generate_hypothetical_doc()  ← LLM γράφει ένα υποθετικό passage
      │    prompt: "Write a passage that answers: {question}"
      │    output: "Mira is a young girl who lives in Loopwick..."
      ↓
ChromaDB.similarity_search(hypothetical_doc_embedding, k=4)
      │    ← πλουσιότερο embedding από σύντομη ερώτηση!
      ↓
format_docs() → context string
      ↓
QA Prompt (system + context + history + original_question)
      ↓
ChatOpenAI (streaming=True) → token stream
      ↓
hypothetical_doc → εμφανίζεται στο HyDE Accordion του UI
```

**Γιατί HyDE βελτιώνει το retrieval:**
> Μια σύντομη ερώτηση ("Who is Mira?") παράγει αδύναμο embedding.
> Ένα πλήρες passage ("Mira is a young girl...") παράγει πολύ πλουσιότερο embedding
> που ταιριάζει καλύτερα με τα αποθηκευμένα chunks.

---

**Streaming events:**
```python
{"type": "token", "content": "Mira"}      # κάθε token
{"type": "token", "content": " lives"}
...
{"type": "done",
 "sources": [...],
 "token_info": "~150 tokens | ~$0.00002",
 "hypothetical_doc": "Mira is a young girl..."  # ή None αν use_hyde=False
}
```

---

### `01_rag_concepts.ipynb` — Εκπαιδευτικό Notebook

Standalone notebook για την κατανόηση των RAG concepts.
**Δεν εξαρτάται** από τα αρχεία του project — τρέχει ανεξάρτητα.

---

## 🔁 Data Flow — Πλήρης Ροή

```
INGESTION:
  Αρχείο → ingestor._load() → LangChain Docs
          → RecursiveCharacterTextSplitter → chunks
          → OpenAIEmbeddings → vectors
          → ChromaDB.add_documents() → αποθηκεύεται στο chroma_db/

QUERY — Standard (use_hyde=False):
  Ερώτηση + Ιστορικό → chain_builder.answer_stream(use_hyde=False)
    → get_query(): [history?] → GPT reformulates → standalone question
    → embed(question) → ChromaDB.similarity_search(k=4) → top-4 chunks
    → format_docs() → context string
    → ChatPromptTemplate → full prompt
    → ChatOpenAI(stream=True) → token stream
    → Gradio chatbot (token-by-token display)
    → {"type": "done", sources, token_info, hypothetical_doc: None}

QUERY — HyDE (use_hyde=True):
  Ερώτηση → chain_builder.answer_stream(use_hyde=True)
    → _generate_hypothetical_doc(question)
        → LLM: "Write a passage that answers: {question}"
        → hypothetical_doc = "Mira is a young girl who lives in..."
    → embed(hypothetical_doc) → ChromaDB.similarity_search(k=4) → top-4 chunks
    → format_docs() → context string
    → ChatPromptTemplate (original question, NOT hypothetical_doc) → full prompt
    → ChatOpenAI(stream=True) → token stream
    → Gradio chatbot + HyDE Accordion (token-by-token display)
    → {"type": "done", sources, token_info, hypothetical_doc: "Mira is..."}
```

