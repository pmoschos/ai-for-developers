from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env", override=True)

llm = ChatOpenAI(model="gpt-4o-mini")

response = llm.invoke("Explain what RAG is in one paragraph.")
print(response.content)