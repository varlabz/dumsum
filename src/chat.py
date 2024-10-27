import argparse
import json
import os
from typing import Final
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate

HR_FILE: Final = "data/hr.md"
SKILLS_FILE: Final = "data/skills.md"
RESUME_FILE: Final = "data/resume.md"
DEFAULTS_FILE: Final = "data/defaults.yaml"

def read_file_content(file_path: str) -> str | None:
    with open(file_path, 'r') as file:
        return file.read()

def extract_between_markers(text: str, marker1: str, marker2: str) -> str | None:
    start = text.find(marker1)
    if start == -1:
        return None
    start += len(marker1)
    end = text.find(marker2, start)
    if end == -1:
        return None
    return text[start:end]

def _chat():
    if os.environ.get("OPENAI_API_KEY"):
        print("Using OpenAI")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.5,
        )

    if os.environ.get("GROQ_API_KEY"):
        print("Using Groq")
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=os.environ.get("GROQ_API_KEY"),
            model="llama-3.2-3b-preview",
            temperature=0.5,
        )

    if os.environ.get("ANTHROPIC_API_KEY"):    
        print("Using Anthropic")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            model="claude-3-haiku-20240307",
            temperature=0.5,
        )

    print("Using Ollama")
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model="llama3.2",    
        # model="qwen2.5:14b",
        # model="phi3.5:latest",
        temperature=0,
    )

chat = _chat()

def matcher(job: str):
    system = SystemMessagePromptTemplate.from_template(read_file_content(HR_FILE)).format(JOB_DESCRIPTION=job,)    
    user = HumanMessagePromptTemplate.from_template(read_file_content(RESUME_FILE)).format()                                                       
    prompt_template = ChatPromptTemplate.from_messages([system, user])
    try:
        chain = prompt_template | chat | JsonOutputParser() 
        res = chain.invoke({})
        # print(res)
        return res
    except Exception as ex:
        print(f"Error decoding JSON: {ex}")
        return None    

def answer(skill: str):
    # TODO: problem with ollama and big default 
    # system = SystemMessagePromptTemplate.from_template(read_file_content(SKILLS_FILE)).format(RESUME=read_file_content(RESUME_FILE) + "\n" + read_file_content(DEFAULTS_FILE),)
    system = SystemMessagePromptTemplate.from_template(read_file_content(SKILLS_FILE)).format(RESUME=read_file_content(RESUME_FILE),)
    user = HumanMessagePromptTemplate.from_template(skill).format()                                                       
    prompt_template = ChatPromptTemplate.from_messages([system, user])
    try:
        chain = prompt_template | chat | JsonOutputParser() 
        res = chain.invoke({})
        # print(res)
        return res
    except Exception as ex:
        print(f"Error decoding JSON: {ex}")
        return None    

# testing
def _main_chat():
    parser = argparse.ArgumentParser(description="Chat with AI")
    parser.add_argument("-j", required=False, type=str, help="Job description file")
    parser.add_argument("-s", required=False, type=str, help="skill")
    args = parser.parse_args()
    if hasattr(args, 'j') and args.j:
        return matcher(read_file_content(args.j))
    if hasattr(args, 's') and args.s:
        return answer(args.s)

if __name__ == "__main__":
    print(f"{_main_chat()}")