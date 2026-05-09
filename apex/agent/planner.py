import json 
from apex.models.fallback import llm_safe
from apex.models.router import CHAT_MODELS

SYSTEM = """You are a planner. Look at the user message and pick ONE tool.

Tools available:
- run_cmd             → user wants to run, execute, install something
- find_relevant_code  → user wants to find, search, locate code in project
- read_file           → user wants to read or open a specific file
- write_file          → user wants to create or save a file
- fix_code            → user wants to fix, debug, correct existing code
- delete_file         → user wants to delete a file
- list_dir            → user wants to see files in a folder
- answer              → just answer directly, no tool needed

Reply ONLY with JSON: {"tool": "tool_name"}
No explanation. No markdown."""

def plan(user_message : str) -> str:
    messages = [
        {"role" : "system" , "content" : SYSTEM},
        {"role" : "user" , "content" : user_message}
    ]


    response = llm_safe(
        messages, 
        model_list = CHAT_MODELS,
        max_tokens = 40,
        )

    if response is "None":
        return "answer"

    try:
        text = response.choices[0].message.content.strip()
        return json.loads(text)["tool"]
    except:
        return "answer"