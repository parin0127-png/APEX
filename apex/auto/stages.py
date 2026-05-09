import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apex.models.fallback import llm_safe
from apex.models.router import AUTO_MODELS
from apex.tools.tools import REGISTRY
import json
import subprocess

SERVER = [
"flask",
"uvicorn",
"fastapi",
"django",
"gunicorn",
"python app.py",
"npm start",
"npm run",
"node",
"nodemon",
"spring",
"mvn spring-boot:run",
"java -jar",
"dotnet run",
"rails server",
"php artisan serve",
"go run",
"cargo run",
]
def stage_run_cmd(goal , last_result):
    prompt = """Command line expert. Return only the raw command, nothing else.
If last result has a filename like hello.py, return: python hello.py"""
    messages = [
        {"role" : "system" , "content" : prompt},
        {"role" : "user" , "content" : f"Goal : {goal} \n Last result : {last_result[:200]} \n command should I run?"}
    ]
    response = llm_safe(messages, model_list = AUTO_MODELS, max_tokens = 50)
    
    text = response.choices[0].message.content
    command = text.strip()
    if any(keyword in command.lower() for keyword in SERVER):
        subprocess.Popen(command, shell=True)
        return f"Server started in background: {command}"
        
    result = REGISTRY["run_cmd"](command)
    if result is None or result == "":
        result = "Command executed : " + command

    return result

def stage_write_file(goal , last_result):
    prompt = f"""Coding expert. Return ONLY JSON: {{"filename": "name", "content": "code"}}. No markdown."""
    messages = [
        {"role" : "system" , "content" : prompt},
        {"role" : "user" , "content" : f"Goal : {goal}"}
    ]
    response = llm_safe(messages, model_list = AUTO_MODELS, max_tokens = 2000)

    try : 
        text = response.choices[0].message.content

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        text = text.strip()
        data = json.loads(text)
        filename = data["filename"]
        content = data["content"]
        REGISTRY["write_file"](data["filename"] , data["content"])
        return f"Filename : " + filename
    except : 
        print("> failed to parse write_file response")
        return "failed to write file"

def stage_read_file(goal, last_result):
    prompt = """you are a file navigation expert.
        look at the goal and last result and return only the filename that needs to be read.
        return only the filename like: app.py or src/main.py
        no explanation, no markdown, nothing else.
        """

    messages = [
        {"role" : "system" , "content" : prompt},
        {"role" : "user" , "content" :  f"Goal : {goal} \n Last result : {last_result} \n What should i read ?"}
    ]

    response = llm_safe(messages, model_list = AUTO_MODELS, max_tokens = 50)

    text = response.choices[0].message.content
    data = text.strip()
    result = REGISTRY["read_file"](data)
    return result

def stage_fix_code(goal, last_result):
    prompt = """Code fixing expert. Return ONLY JSON: {"filename": "name", "content": "fixed code"}. No markdown."""

    messages = [
        {"role" : "system" , "content" : prompt},
        {"role" : "user" , "content" : f"Goal : {goal} \n Error : {last_result[:500]}"}
    ]

    response = llm_safe(messages, model_list = AUTO_MODELS, max_tokens = 2000)

    try :
        text = response.choices[0].message.content

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        text = text.strip()
        data = json.loads(text)
        filename = data["filename"]
        content = data["content"]
        REGISTRY["write_file"](data["filename"] , data["content"])
        return "code fixed: " + filename
    except : 
        print("> failed to fix code")
        return "> failed to fix code"