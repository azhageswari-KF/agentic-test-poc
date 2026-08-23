"""
Single place that creates the LLM client every agent uses.

Points at a local Ollama model by default so the POC has zero cloud
dependency. Swap OLLAMA_MODEL in .env to try a different open model
(e.g. qwen2.5-coder if generic llama3.1 struggles with Karate syntax).
"""

import os
from dotenv import load_dotenv
load_dotenv()

def get_llm(temperature: float = 0.1):
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            temperature=temperature,
        )
    from langchain_community.chat_models import ChatOllama
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=temperature,
    )