from argparse import Namespace, ArgumentParser, FileType
import argparse
import os
import sys
from typing import List, Final
from langchain_openai import OpenAI
from langchain.globals import set_verbose
from langchain.globals import set_debug
import yaml
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate

HR_FILE: Final = "data/hr.md"
SKILLS_FILE: Final = "data/skills.md"
RESUME_FILE: Final = "data/resume.md"

def read_file_content(file_path) -> str | None:
    with open(file_path, 'r') as file:
        return file.read()

def extract_between_markers(text, marker1, marker2):
    start = text.find(marker1)
    if start == -1:
        return None
    start += len(marker1)
    end = text.find(marker2, start)
    if end == -1:
        return None
    return text[start:end]

