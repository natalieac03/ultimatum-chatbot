import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


def get_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("A chave da Open Router não definida no ambiente.")

    return AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-OpenRouter-Title": "CH5 Local LLM Service",
        },
    )
