# Module 4: Retrieval-Augmented Generation (RAG)

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand why RAG is essential for custom knowledge applications
- Build a complete document ingestion pipeline
- Work with embeddings and vector databases
- Create a Q&A bot that answers from your own documents

## 📚 Key Concepts

### Why RAG?

LLMs have a **knowledge cutoff** - they only know what was in their training data. RAG solves this by:

1. **Retrieving** relevant information from your own documents
2. **Augmenting** the prompt with this context
3. **Generating** accurate answers grounded in your data

### The RAG Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     INGESTION PHASE                         │
├─────────────────────────────────────────────────────────────┤
│  Document → Chunking → Embedding → Vector Database          │
│    📄         ✂️          🔢           💾                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      QUERY PHASE                            │
├─────────────────────────────────────────────────────────────┤
│  Question → Embed → Search → Retrieve → Augment → Generate  │
│     ❓        🔢       🔍       📋        📝        💡     │
└─────────────────────────────────────────────────────────────┘
```

### Key Terms

| Term | Definition |
|------|------------|
| **Embedding** | A vector (list of numbers) representing the meaning of text |
| **Vector Database** | Database optimized for similarity search on vectors |
| **Chunk** | A segment of a document (typically 500-1000 tokens) |
| **Semantic Search** | Finding content by meaning, not just keywords |
| **Context Window** | The retrieved chunks passed to the LLM |

### Chunking Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| **Fixed Size** | Split every N characters | Simple documents |
| **Recursive** | Split by paragraphs, then sentences | General use |
| **Semantic** | Split by topic/meaning | Complex documents |

## 🔬 Hands-On Project: Document Q&A Bot

Build a complete Q&A system that answers questions based on your documents.

### Project Structure

```
module_04_rag/
├── README.md                          # This file
├── concepts/
│   ├── embeddings_explained.md        # Visual guide to embeddings
│   ├── vector_databases.md            # ChromaDB tutorial
│   └── chunking_strategies.md         # Text splitting approaches
│
├── document_qa_bot/
│   ├── app.py                         # Main CLI application
│   ├── config.py                      # Configuration
│   │
│   ├── ingestion/
│   │   ├── loader.py                  # PDF/TXT file loader
│   │   ├── chunker.py                 # Text chunking strategies
│   │   └── embedder.py                # Embedding generation
│   │
│   ├── retrieval/
│   │   ├── vector_store.py            # ChromaDB wrapper
│   │   └── retriever.py               # Semantic search
│   │
│   ├── generation/
│   │   ├── qa_chain.py                # RAG chain implementation
│   │   └── prompts.py                 # QA prompt templates
│   │
│   ├── sample_docs/                   # Sample documents
│   │   └── README.md                  # Add your docs here
│   │
│   └── chroma_db/                     # Vector database storage
│
└── exercises/
    └── challenges.md
```

### Quick Start

```bash
# Navigate to the module
cd module_04_rag/document_qa_bot

# Ingest a document
python app.py ingest sample_docs/your_document.pdf

# Ask questions
python app.py ask "What is the main topic of the document?"

# Interactive chat mode
python app.py chat
```

## 💡 Implementation Details

### Embedding Models

We use OpenAI's `text-embedding-3-small`:
- 1536 dimensions
- Good balance of quality and cost
- ~$0.02 per 1M tokens

### ChromaDB

A lightweight, local vector database:
- No external dependencies
- Persistent storage
- Fast similarity search

### Chunking Configuration

Default settings (adjustable in `config.py`):
- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Separator: paragraphs first, then sentences

## ✅ Checklist

Before moving to Module 5:
- [ ] Successfully ingest a document
- [ ] Query the document and get relevant answers
- [ ] Understand how embeddings represent meaning
- [ ] Know when to use different chunking strategies
- [ ] Experiment with chunk size parameters

## 🔗 Resources

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)

---

**Next Module**: [Module 5: AI Agents →](../module_05_agents/README.md)
