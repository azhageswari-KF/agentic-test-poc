# """
# Single place that creates the LLM client every agent uses.

# Points at a local Ollama model by default so the POC has zero cloud
# dependency. Swap OLLAMA_MODEL in .env to try a different open model
# (e.g. qwen2.5-coder if generic llama3.1 struggles with Karate syntax).
# """

# import os
# from dotenv import load_dotenv
# # from langchain_community.chat_models import 
# from langchain_ollama import ChatOllama

# load_dotenv()


# def get_llm(temperature: float = 0.1):
#     model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
#     base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
#     return ChatOllama(model=model, base_url=base_url, temperature=temperature)


import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_llm(temperature: float = 0.1):
    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Get a free key at "
            "https://aistudio.google.com/apikey and add it to your .env file "
            "as GOOGLE_API_KEY=your-key-here"
        )

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
    )

def get_text(response) -> str:
    """Normalizes .content whether it's a plain string or a list of parts."""
    content = response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(item.get("text", ""))
        return "".join(parts)
    return str(content)