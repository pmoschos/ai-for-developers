# Module 3: Building Applications - The AI Architecture Stack

## 🎯 Learning Objectives

By the end of this module, you will:
- Design and build production-ready AI-powered API endpoints
- Implement reliability patterns (retries, timeouts, rate limiting)
- Manage costs and track token usage
- Build a complete FastAPI application wrapping an LLM

## 📚 Key Concepts

### The AI Integration Stack

```
┌─────────────────────────────────────────────┐
│              Client Application             │
├─────────────────────────────────────────────┤
│              API Layer (FastAPI)            │
│   - Input validation (Pydantic)             │
│   - Rate limiting                           │
│   - Authentication                          │
├─────────────────────────────────────────────┤
│            Middleware Layer                 │
│   - Cost tracking                           │
│   - Logging                                 │
│   - Error handling                          │
├─────────────────────────────────────────────┤
│              LLM Client                     │
│   - Retries with backoff                    │
│   - Timeout handling                        │
│   - Provider abstraction                    │
├─────────────────────────────────────────────┤
│           LLM Provider (OpenAI)             │
└─────────────────────────────────────────────┘
```

### Common AI Integration Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Chatbot** | Conversational UI | Customer support |
| **Content Generator** | Create text/code | Marketing copy |
| **Classifier** | Categorize inputs | Sentiment analysis |
| **Extractor** | Pull structured data | Parse invoices |
| **Summarizer** | Condense content | Meeting notes |
| **Transformer** | Convert formats | Style transfer |

### Production Considerations

#### Reliability
- API rate limits and quotas
- Network timeouts
- Model availability
- Graceful degradation

#### Cost Management
- Token counting and budgeting
- Model selection (cost vs. quality)
- Caching strategies
- Request batching

#### Performance
- Streaming responses
- Async processing
- Connection pooling
- Response caching

## 🔬 Hands-On Project

### Build a Multi-Purpose AI API

You'll build a FastAPI application with three endpoints:

| Endpoint | Purpose | Input → Output |
|----------|---------|----------------|
| `POST /summarize` | Text summarization | Long text → Summary |
| `POST /sentiment` | Sentiment analysis | Text → Sentiment + Score |
| `POST /copywriter` | Marketing copy | Product info → Copy variants |

### Project Structure

```
module_03_ai_architecture/
├── README.md                    # This file
├── concepts/
│   ├── patterns.md              # AI integration patterns
│   └── reliability.md           # Error handling guide
├── app/
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration
│   ├── models.py                # Pydantic models
│   ├── llm_client.py            # LLM client wrapper
│   ├── routers/
│   │   ├── summarize.py         # Summarization endpoint
│   │   ├── sentiment.py         # Sentiment endpoint
│   │   └── copywriter.py        # Copywriting endpoint
│   └── middleware/
│       ├── rate_limiter.py      # Rate limiting
│       ├── cost_tracker.py      # Token/cost tracking
│       └── error_handler.py     # Error handling
├── tests/
│   └── test_endpoints.py        # API tests
└── run.py                       # Easy startup script
```

### Running the Application

```bash
# Navigate to module
cd module_03_ai_architecture

# Run the server
python run.py

# Or with uvicorn directly
uvicorn app.main:app --reload --port 8000
```

### Testing the Endpoints

```bash
# Summarization
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here...", "max_length": 100}'

# Sentiment Analysis
curl -X POST "http://localhost:8000/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "I absolutely love this product!"}'

# Copywriting
curl -X POST "http://localhost:8000/copywriter" \
  -H "Content-Type: application/json" \
  -d '{"product_name": "AI Helper", "description": "An AI assistant", "tone": "professional"}'
```

## 💡 Key Implementation Details

### LLM Client Abstraction

The `llm_client.py` provides:
- Retry logic with exponential backoff
- Timeout handling
- Token counting
- Cost estimation
- Easy provider switching

### Cost Tracking

Every request is tracked with:
- Input/output token counts
- Estimated cost
- Request duration
- Model used

### Error Handling

Graceful handling of:
- Rate limits (429)
- Timeouts
- Invalid inputs
- Model errors

## ✅ Checklist

Before moving to Module 4:
- [ ] Successfully run the FastAPI application
- [ ] Test all three endpoints
- [ ] Understand the LLM client abstraction
- [ ] Review the cost tracking middleware
- [ ] Try adding a new endpoint

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)

---

**Next Module**: [Module 4: RAG →](../module_04_rag/README.md)
