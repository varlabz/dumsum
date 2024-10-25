import os
from typing import Final

use_openai: Final = True if os.environ.get("OPENAI_API_KEY") else False
use_groq: Final = True if os.environ.get("GROQ_API_KEY") else False
if not use_openai and not use_groq:
    print("Using Ollama")

def answer(skill: str):
    if use_openai:
        import chat_openai
        return chat_openai.answer(skill)
    elif use_groq:
        import chat_groq
        return chat_groq.answer(skill)
    else: 
        import chat_ollama
        return chat_ollama.answer(skill)
      

def matcher(job: str):
    if use_openai:
        import chat_openai
        return chat_openai.matcher(job)
    elif use_groq:
        import chat_groq
        return chat_groq.matcher(job)
    else: 
        import chat_ollama
        return chat_ollama.matcher(job)
