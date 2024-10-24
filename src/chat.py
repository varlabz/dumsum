from typing import Final

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

