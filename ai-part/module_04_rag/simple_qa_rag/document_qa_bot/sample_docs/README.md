# Sample Documents

Place your documents here for the Q&A bot to learn from.

## Supported Formats

- **PDF** (`.pdf`) - Research papers, reports, books
- **Text** (`.txt`) - Plain text documents
- **Markdown** (`.md`) - Documentation, notes
- **Word** (`.docx`) - Microsoft Word documents

## Usage

```bash
# From the document_qa_bot directory
python app.py ingest sample_docs/your_document.pdf

# Or ingest all documents in this folder
python app.py ingest sample_docs/
```

## Sample Document

Here's some sample content about AI to test with:

---

# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence (AI) that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.

## Types of Machine Learning

### Supervised Learning
In supervised learning, the algorithm is trained on labeled data. The training data includes both the input and the desired output. Examples include:
- Classification (spam detection, image recognition)
- Regression (price prediction, weather forecasting)

### Unsupervised Learning
Unsupervised learning works with unlabeled data. The algorithm tries to find patterns and relationships in the data. Examples include:
- Clustering (customer segmentation)
- Dimensionality reduction (feature extraction)

### Reinforcement Learning
In reinforcement learning, an agent learns by interacting with an environment and receiving rewards or penalties for its actions. Examples include:
- Game playing (chess, Go)
- Robotics (autonomous navigation)

## Large Language Models

Large Language Models (LLMs) are a type of machine learning model trained on vast amounts of text data. They can understand and generate human-like text. Key characteristics include:

1. **Scale**: Billions of parameters
2. **Training**: Self-supervised learning on internet text
3. **Capabilities**: Text generation, translation, summarization, question answering
4. **Examples**: GPT-4, Claude, Llama, Gemini

LLMs have revolutionized natural language processing and enabled new applications like chatbots, code generation, and content creation.
