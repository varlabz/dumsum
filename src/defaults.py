"""
get/set default values key/value pair
"""
import argparse
import os
from typing import Final
import yaml
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate
from chat import _chat, answer
from common import get_data_file

DEFAULTS: Final = "data/defaults.yaml"
DEFAULTS_FILE: Final = "defaults.md"

def _embeddings():
    if os.environ.get("OPENAI_API_KEY"):
        print("Using OpenAI embeddings")
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    if os.environ.get("GROQ_API_KEY"):
        print("Using Groq embeddings NO")
        return None

    if os.environ.get("ANTHROPIC_API_KEY"):    
        print("Using Anthropic embeddings NO")
        return None

    print("Using Ollama embeddings")
    from langchain_ollama import OllamaEmbeddings
    return OllamaEmbeddings(
        model="mxbai-embed-large",
    )

class Defaults:
    def __init__(self):
        self.chat = _chat()
        self.embeddings = _embeddings()
        self.data = {}
        if not os.path.exists(DEFAULTS):
            self.save()
        with open(DEFAULTS, "r") as file:
            self.data = yaml.safe_load(file)
        if embeddings := self.embeddings:
            texts = [f"{k}:{v}" for k, v in self.data.items()]
            self.vectorstore = Chroma.from_texts(texts=texts, embedding=embeddings)            

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value
        if embeddings := self.embeddings:
            self.vectorstore.add_texts(texts=[f"{key}:{value}"], embedding=embeddings)

    # def pop(self, key):
    #     self.data.pop(key)
    #     if self.embeddings:
    #         self.vectorstore.delete(ids=[key])

    def get(self, key) -> dict:
        if self.embeddings is None:
            if v := self.data.get(key, None):
                return {"question": key, "answer": v, "explanation": "No embeddings"}
            return None
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(key)        
        docs = "\n".join([doc.page_content for doc in docs])
        # print(docs)
        system = SystemMessagePromptTemplate.from_template_file(get_data_file(DEFAULTS_FILE), ["CONTEXT"]).format(CONTEXT=docs,)    
        # print(system)
        user = HumanMessagePromptTemplate.from_template(key).format()                                                       
        prompt_template = ChatPromptTemplate.from_messages([system, user])
        try:
            chain = prompt_template | self.chat | JsonOutputParser() 
            res = chain.invoke({})
            # print(res)
            return res
        except Exception as ex:
            print(f"Error decoding JSON: {ex}")
            print(f">>> failed with defaults. will try with resume")
            return answer(key)

    def save(self):
        with open(DEFAULTS, "w") as file:
            yaml.dump(self.data, file, width=float('inf'), default_flow_style=False, sort_keys=False)  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with defaults")
    parser.add_argument("-s", required=False, type=str, help="skill")
    args = parser.parse_args()
    if hasattr(args, 's') and args.s:
        defaults = Defaults()
        print(defaults.get(args.s))
