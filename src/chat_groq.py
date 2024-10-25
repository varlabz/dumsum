import argparse
import json
import os
from typing import Final
from groq import Groq

from chat_common import HR_FILE, RESUME_FILE, SKILLS_FILE, extract_between_markers, read_file_content

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def matcher(job: str):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": read_file_content(HR_FILE).format(JOB_DESCRIPTION=job,)
            },
            {
                "role": "user",
                "content": read_file_content(RESUME_FILE),
            }
        ],
        model="llama-3.2-3b-preview",
        # model="llama-3.1-70b-versatile",
        temperature=0,
        max_tokens=1024*8,
        # Controls diversity via nucleus sampling: 0.5 means half of all
        # likelihood-weighted options are considered.
        # top_p=1,
        stop=None,
        stream=False,
    )
    try:
        res = chat_completion.choices[0].message.content
        # print(res)
        tmp = extract_between_markers(res, "```json", "```")
        res = tmp if tmp else res    
        tmp = extract_between_markers(res, "```", "```")
        res = tmp if tmp else res    
        ret = json.loads(res)
        return ret
    except Exception as ex:
        print(f"Error decoding JSON: {ex} from {res}")
        return None    

def answer(skill: str):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": read_file_content(SKILLS_FILE).format(RESUME=read_file_content(RESUME_FILE),)
            },
            {
                "role": "user",
                "content": skill,
            }
        ],
        model="llama-3.2-3b-preview",
        # model="llama-3.1-70b-versatile",
        # model="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=1024*8,
        # Controls diversity via nucleus sampling: 0.5 means half of all
        # likelihood-weighted options are considered.
        # top_p=1,
        stop=None,
        stream=False,
    )
    try:
        res = chat_completion.choices[0].message.content
        # print(res)
        tmp = extract_between_markers(res, "```json", "```")
        res = tmp if tmp else res    
        tmp = extract_between_markers(res, "```", "```")
        res = tmp if tmp else res    
        ret = json.loads(res)
        return ret
    except Exception as ex:
        print(f"Error decoding JSON: {ex} from {res}")
        return None    

# testing
def main_chat():
    parser = argparse.ArgumentParser(description="Chat with AI")
    parser.add_argument("-j", required=False, type=str, help="Job description file")
    parser.add_argument("-s", required=False, type=str, help="skill")
    args = parser.parse_args()
    if hasattr(args, 'j') and args.j:
        return matcher(read_file_content(args.j))
    if hasattr(args, 's') and args.s:
        return answer(args.s)

if __name__ == "__main__":
    print(main_chat())