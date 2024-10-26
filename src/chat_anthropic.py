import argparse
import json
import os
import anthropic

from chat_common import HR_FILE, RESUME_FILE, SKILLS_FILE, extract_between_markers, read_file_content

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

def matcher(job: str):
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        # model="claude-3-5-sonnet-latest",
        temperature=0.8,
        max_tokens=1024*4,
        system=read_file_content(HR_FILE).format(JOB_DESCRIPTION=job,),
        messages=[
            {
                "role": "user",
                "content": read_file_content(RESUME_FILE),
            },
        ],
    )
    try:
        res = message.content[0].text
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
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        temperature=0,
        max_tokens=1024*2,
        system=read_file_content(SKILLS_FILE).format(RESUME=read_file_content(RESUME_FILE),),
        messages=[
            {
                "role": "user",
                "content": skill,
            }
        ],
    )
    try:
        res = message.content[0].text
        print(res)
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
    print(f">>>> {main_chat()}")