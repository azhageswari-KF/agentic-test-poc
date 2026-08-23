"""
Single place that creates the LLM client every agent uses.

Points at a local Ollama model by default so the POC has zero cloud
dependency. Swap OLLAMA_MODEL in .env to try a different open model
(e.g. qwen2.5-coder if generic llama3.1 struggles with Karate syntax).
"""

import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama

load_dotenv()


def get_llm(temperature: float = 0.1):
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ChatOllama(model=model, base_url=base_url, temperature=temperature)
