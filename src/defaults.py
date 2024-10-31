"""
get/set default values key/value pair
"""
import argparse
import os
from typing import Final
from langchain_text_splitters import MarkdownHeaderTextSplitter, MarkdownTextSplitter, RecursiveCharacterTextSplitter
import yaml
from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from chat import RESUME_FILE, _chat, answer, read_file_content
from common import get_data_file

DEFAULTS: Final = "data/defaults.yaml"
DEFAULTS_SYSTEM_FILE: Final = "defaults-system.md"
DEFAULTS_USER_FILE: Final = "defaults-user.md"

def _embeddings():
    if key:=os.environ.get("OPENAI_API_KEY"):
        print("Using OpenAI embeddings")
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            api_key=key,
        )

    if os.environ.get("GROQ_API_KEY"):
        print("Using Groq embeddings NO")
        return None

    if os.environ.get("ANTHROPIC_API_KEY"):    
        print("Using Anthropic embeddings NO")
        return None
    
    if key:=os.environ.get("JINA_API_KEY"):
        print("Using JinaAI embeddings")
        from langchain_community.embeddings import JinaEmbeddings
        return JinaEmbeddings(
            jina_api_key=key, 
        )

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
        if (embeddings := self.embeddings):
            docs = UnstructuredMarkdownLoader(RESUME_FILE, ).load_and_split(text_splitter=MarkdownTextSplitter())
            docs = filter_complex_metadata(docs)    # remove arrays from metadata
            self.vectorstore = Chroma.from_documents(documents=docs, embedding=self.embeddings)
            if texts := [f"{k}:{v}" for k, v in self.data.items()]:
                self.vectorstore.add_texts(texts=texts, embedding=embeddings, ids=[k for k in self.data.keys()])            

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value
        if embeddings := self.embeddings:
            self.vectorstore.delete(ids=[key])
            self.vectorstore.add_texts(texts=[f"{key}:{value}"], embedding=embeddings, ids=[key])

    def get(self, key, options: list = []) -> dict:
        if self.embeddings is None:
            if v := self.data.get(key, None):
                return {"question": key, "answer": v, "explanation": "No embeddings"}
            return None
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 6})
        docs = retriever.invoke(key)        
        docs = "\n".join([doc.page_content for doc in docs])
        system = SystemMessagePromptTemplate.from_template_file(get_data_file(DEFAULTS_SYSTEM_FILE), ["CONTEXT"]).format(
            CONTEXT=docs,)    
        user = HumanMessagePromptTemplate.from_template_file(get_data_file(DEFAULTS_USER_FILE), ['QUESTION', 'OPTIONS']).format(
            QUESTION=key, OPTIONS="\n".join([f"- {i}" for i in options]))
        prompt_template = ChatPromptTemplate.from_messages([system, user])
        try:
            chain = prompt_template | self.chat | JsonOutputParser() 
            res = chain.invoke({})
            # print(res)
            return res
        except Exception as ex:
            print(f"Error decoding JSON: {ex}")
            return None

    def save(self):
        with open(DEFAULTS, "w") as file:
            yaml.dump(self.data, file, width=float('inf'), default_flow_style=False, sort_keys=False)  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with defaults")
    parser.add_argument("-s", required=False, type=str, help="skill")
    parser.add_argument('-a', nargs='*', help='An array of values')
    args = parser.parse_args()
    if hasattr(args, 's') and args.s:
        defaults = Defaults()
        print(defaults.get(args.s, args.a if args.a else []))
