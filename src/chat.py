import argparse
import json
import os
from typing import Final
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate
from langchain_core.messages import HumanMessage

from common import get_data_file

HR_FILE: Final = "hr.md"
HR_FALLBACK_FILE: Final = "hr-fallback.md"
SKILLS_FILE: Final = "skills.md"
RESUME_FILE: Final = "data/resume.md"       # should use user updated resume file
DEFAULTS: Final = "data/defaults.yaml"
DEFAULTS_SYSTEM_FILE: Final = "defaults-system.md"
DEFAULTS_USER_FILE: Final = "defaults-user.md"

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
    if key:=os.environ.get("XAI_API_KEY"):
        print("Using XAI")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=key,
            base_url="https://api.x.ai/v1/",
            model=os.getenv("XAI_MODEL", "grok-beta"),
            temperature=0.1,
            seed=1234,
        )

    if key:=os.environ.get("GROQ_API_KEY"):
        print("Using Groq")
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=key,
            # model="llama-3.2-3b-preview",
            model=os.getenv("GROQ_MODEL", "deepseek-r1-distill-llama-70b"),
            temperature=0.1,
        )

    if key:=os.environ.get("ANTHROPIC_API_KEY"):    
        print("Using Anthropic")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            api_key=key,
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
            temperature=0.1,
        )

    if key:=os.environ.get("GITHUB_TOKEN"):
        # check https://github.com/marketplace/models
        print("Using GithubOpenAI")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=key,
            # model="gpt-4o",
            model=os.getenv("GITHUB_MODEL", "gpt-4o-mini"),
            temperature=0.1,
            seed=100,
        )

    if key:=os.environ.get("OPENAI_API_KEY"):
        print("Using OpenAI")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=key,
            # model="gpt-4o",
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.1,
            seed=100,
        )
    
    # print("Using Llama.cpp")
    # import warnings
    # from huggingface_hub import hf_hub_download
    # from langchain_community.chat_models import ChatLlamaCpp
    # warnings.filterwarnings("ignore", message="ggml_metal_init")
    # warnings.filterwarnings("ignore", category=UserWarning)
    # model_path = hf_hub_download(
    #     repo_id="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF", 
    #     filename="qwen2.5-coder-7b-instruct-q4_0.gguf", 
    # )
    # return ChatLlamaCpp(
    #     model_path=model_path,
    #     temperature=0.1,      
    #     n_ctx=8096,           
    #     max_tokens=1024,      
    #     seed=100,
    #     verbose=False,
    #     streaming=False,
    #     n_gpu_layers=0,
    # )

    print("Using Ollama")
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:latest"),
        temperature=0.1,
        num_ctx=8096,
        seed=100,
        keep_alive="15m", 
    )

def matcher(job: str):
    chat = _chat()
    system = SystemMessagePromptTemplate.from_template_file(
        get_data_file(HR_FILE), ['JOB_DESCRIPTION']).format(JOB_DESCRIPTION=job,)    
    user = HumanMessagePromptTemplate.from_template_file(RESUME_FILE, []).format()                                                       
    prompt_template = ChatPromptTemplate.from_messages([system, user])
    try:
        chain = prompt_template | chat | JsonOutputParser() 
        res = chain.invoke({})
        # print(res)
        return res
    except Exception as ex:
        print(f"Error decoding JSON: {ex}")
        # after hallucination take ex and call chat to convert response to json structure with expected format
        return matcher_fallback(ex.args[0])

def matcher_fallback(answer: str):
    chat = _chat()
    system = SystemMessagePromptTemplate.from_template_file(get_data_file(HR_FALLBACK_FILE), []).format()    
    user = HumanMessage(content=answer)                                                       
    prompt_template = ChatPromptTemplate.from_messages([system, user])
    try:
        chain = prompt_template | chat | JsonOutputParser() 
        res = chain.invoke({})
        # print(res)
        return res
    except Exception as ex:
        print(f"Error decoding JSON: {ex}")
        return None    

def answer(skill:str, options: list = []) -> dict:
    chat = _chat()
    system = SystemMessagePromptTemplate.from_template_file(
        get_data_file(SKILLS_FILE), ['RESUME', 'SKILLS']).format(
            RESUME=read_file_content(RESUME_FILE),
            SKILLS=read_file_content(DEFAULTS), )
    user = HumanMessagePromptTemplate.from_template_file(
        get_data_file(DEFAULTS_USER_FILE), ['QUESTION', 'OPTIONS']).format(
            QUESTION=skill, 
            OPTIONS="\n".join([f"- {i}" for i in options]))
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
if __name__ == "__main__":
    def _main_chat():
        parser = argparse.ArgumentParser(description="Chat with AI")
        parser.add_argument("-j", required=False, type=str, help="Job description file")
        parser.add_argument("-s", required=False, type=str, help="skill")
        parser.add_argument("-f", required=False, type=str, help="fallback")
        parser.add_argument('-a', nargs='*', help='An array of values')
        args = parser.parse_args()
        if hasattr(args, 'j') and args.j:
            return matcher(read_file_content(args.j))
        if hasattr(args, 'f') and args.f:
            return matcher_fallback(args.f)
        if hasattr(args, 's') and args.s:
            return answer(args.s, args.a if args.a else [])
    
    print(f"{_main_chat()}")