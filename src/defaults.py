"""
get/set default values key/value pair
"""
import argparse
import os
import yaml
from chat import DEFAULTS, answer

# def _embeddings():
#     if key:=os.environ.get("GITHUB_TOKEN"):
#         print("Using GithubOpenAI embeddings")
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             base_url="https://models.inference.ai.azure.com",
#             model="text-embedding-3-large",
#             api_key=key,
#         )

#     if key:=os.environ.get("OPENAI_API_KEY"):
#         print("Using OpenAI embeddings")
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             api_key=key,
#         )

#     # if os.environ.get("GROQ_API_KEY"):
#     #     print("Using Groq embeddings NO")
#     #     return None

#     # if os.environ.get("ANTHROPIC_API_KEY"):    
#     #     print("Using Anthropic embeddings NO")
#     #     return None
    
#     # if key:=os.environ.get("JINA_API_KEY"):
#     #     print("Using JinaAI embeddings")
#     #     from langchain_community.embeddings import JinaEmbeddings
#     #     return JinaEmbeddings(
#     #         jina_api_key=key, 
#     #     )

#     print("Using Ollama embeddings")
#     from langchain_ollama import OllamaEmbeddings
#     return OllamaEmbeddings(
#         model="mxbai-embed-large",
#         # model="nomic-embed-text",
#     )

class Defaults:
    def __init__(self):
        self.data = {}
        if not os.path.exists(DEFAULTS):
            self.save()

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def save(self):
        timestamp = os.path.getmtime(DEFAULTS)
        if timestamp != self.timestamp:
            print(f">>> {DEFAULTS} has been modified. Will use updated on next position")
            return
        with open(DEFAULTS, "w") as file:
            yaml.dump(self.data, file, width=float('inf'), default_flow_style=False, sort_keys=False)  
            self.timestamp = os.path.getmtime(DEFAULTS)

    def load(self):
        with open(DEFAULTS, "r") as file:
            self.data = yaml.safe_load(file)
            self.timestamp = os.path.getmtime(DEFAULTS)

    def get(self, key, options: list = []) -> dict:
        if v := answer(key, options):
            self[key] = v["answer"]
            return v
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with defaults")
    parser.add_argument("-s", required=False, type=str, help="skill")
    parser.add_argument('-a', nargs='*', help='An array of values')
    args = parser.parse_args()
    if 's' in args and args.s:
        defaults = Defaults()
        defaults.load()
        print(defaults.get(args.s, args.a if args.a else []))
