from dotenv import load_dotenv
from langsmith import traceable # pip install langsmith
from openai import OpenAI
from pathlib import Path

_env_path = Path(".env")
load_dotenv(dotenv_path=_env_path, override=True)

client = OpenAI()

@traceable(name="generate_answer", run_type="llm")
def generate_answer(question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

@traceable(name="addition_calc", run_type="parser")
def my_add(a, b):
    return a + b

answer = generate_answer("Explain Python decorators.")
print(answer)

result = my_add(10, 20)
print(result)