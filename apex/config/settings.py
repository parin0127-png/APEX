import os 
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rich.console import Console
from rich.panel import Panel
import json
import os

console = Console()

CONFIG_PATH = os.path.join(os.path.expanduser("~") , ".apex" , "config.json")

def create_config() -> dict:
    """
        Asks user setup questions on first run and save to config.json

        Returns:
            config dict
    """

    console.print(Panel("> Welcome to APEX ⚡", style="bold blue", border_style="blue"))
    print("> Get GROQ API key       -> https://console.groq.com ")
    print("> Get Mistral API key    -> https://console.mistral.ai")
    api_key = input("> Groq API key : ") 
    mistral_key = input("> Mistral API key : ")

    print("> Just 2 quick questions ")
    print("> --------------- Your experience level ---------------")
    print("> 1. Beginner ")
    print("> 2. Intermediate ")
    print("> 3. Advance ")

    level_map = {
        "1" : "beginner",
        "2" : "intermediate",
        "3" : "advance"
    }

    while True:
        choice = input("> Enter your experience level : ")
        if choice in level_map:
            default_map = level_map[choice]
            break
        print("> Choice between -> '1' , '2' or '3' ")

    print("> Allow APEX to run commands automatically ? ")
    print("> Yes -> APEX can run commands freely. ")
    print("> No  -> APEX asks you every time. ")

    while True:
        choice = input("> Allow (yes / no) : ").strip().lower()
        if choice in ["yes" , "n"]:
            auto_run = choice == 'yes'
            break
        print("> Choose between Yes or No ")

    config = {
        "default_level" : default_map,
        "auto_run_command" : auto_run,
        "auto_mode" : False,
        "api_key" : api_key,
        "mistral_api_key" : mistral_key,
    }

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok = True)

    with open(CONFIG_PATH, "w" , encoding = "utf-8") as f :
        json.dump(config, f, indent = 4)

    print("> --------------- APEX is ready ---------------")

    return config

def load_config() -> dict:
    """Load config from file. Create it if first run

        Results : 
            config dict
    """

    if not os.path.exists(CONFIG_PATH):
        return create_config()
    
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)
    
    missing_key = False
    for key in ["github_token", "mistral_api_key"]:
        if key not in config:
            val = input(f"> {key}: ").strip()
            config[key] = val
            missing_key = True

    if missing_key:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)



config = load_config() 

icon = "⚙️  "
SENSITIVE_KEY = {"api_key" , "mistral_api_key", "github_token"}

def mask(value : str) -> str:
    return value[:4] + "*******" if len(value) > 4 else "*******"

def save():
    with open(CONFIG_PATH, "w" , encoding = "utf-8") as f:
        json.dump(config, f, indent = 4)

def handle_settings(args : list[str]) -> str:
    if not args or args[0] == "show":
        lines = [f"> {icon} Settings "]
        for k , v in config.items():
            lines.append(f"> -{k} : {mask(str(v)) if k in SENSITIVE_KEY else v}")
        
        return "\n".join(lines)

    if args[0] == "set" and len(args) >= 3:
        config[args[1]] = "".join(args[2:])
        save()

        return f" {icon} Saved"
    

    if args[0] == "delete" and len(args) == 2:
        if args[1] not in config:
            return f"> {icon} 'args[1]' not found "
        del config[args[1]]
        save()

        return f"> {icon} '{args[1]}' deleted !"
     
    return f"> Usage : /setting show | set <key> <value> | delete <key>"