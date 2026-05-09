import json
import os
from datetime import datetime
from apex.models.fallback import llm_safe
from apex.models.router import CHAT_MODELS
from rich.console import Console

console = Console()
MEMORY_PATH = os.path.join(os.path.expanduser("~") ,".apex", "memory.json")

def save_memory(goal , result):
    
    try : 
        with open(MEMORY_PATH, "r") as f:
           memories = json.load(f)

    except:
        memories = []

    entry = {
        "goal" : goal,
        "result" : result,
        "time" : datetime.now().strftime("%Y-%m-%d %H:%M")
    } 

    memories.append(entry)

    memories = memories[-20:]

    os.makedirs(os.path.dirname(MEMORY_PATH) , exist_ok = True)

    try:
        with open(MEMORY_PATH , "w" , encoding = "utf-8") as f:
            json.dump(memories, f , indent = 4)
    except Exception as e:
        return f"Error : {e}"
        
def load_memory():
    try : 
        with open(MEMORY_PATH, "r") as f:
            memories = json.load(f)
            return memories[-5:]
    except :
        return []

def summarize_memory():
    entries = load_memory()

    if not entries:
        return "No previous tasks."
    
    lines = []
    for i , entry in enumerate(entries):
        lines.append(f"Task {i+1}: {entry['goal']} → {entry['result']}")

    formatted = "\n".join(lines)

    system_prompt = "You are a memory summarizer. Summarize these past tasks in exactly 3 lines. Be very brief. Focus on what was built and what happened."

    messages = [
        {"role" : "system" , "content" : system_prompt},
        {"role" : "user" , "content" : formatted}
    ]

    response = llm_safe(messages, model_list = CHAT_MODELS, max_tokens = 150, use_tools = False)

    text = response.choices[0].message.content
    return text
