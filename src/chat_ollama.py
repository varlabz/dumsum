import argparse
import json
import os
import ollama

from chat import HR_FILE, RESUME_FILE, SKILLS_FILE, extract_between_markers, read_file_content

def matcher(job: str):
    response = ollama.chat(
        model='llama3.2', 
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
        stream=False,
        options={
            "temperature": 0, 
            },
    )
    try:
        res = response['message']['content']
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
    response = ollama.chat(
        model='llama3.2', 
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
        stream=False,
        options={
            "temperature": 0, 
            },
    )
    try:
        res = response['message']['content']
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
    # return matcher(read_file_content(args.j))
    return answer(args.s)

if __name__ == "__main__":
    print(main_chat())