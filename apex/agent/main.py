import warnings
warnings.filterwarnings("ignore")
import os
import sys
import re
import platform
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from rich.prompt import Prompt

from apex.config.settings import config, handle_settings, save
from apex.config.help import handle_help
from apex.agent.agent import run_agent
from apex.github.github import handle_github
from apex.watchdog.watchdog import handle_watchdog
from apex.auto.pipelines import run_auto
from apex.tools.tools import write_file
from apex.agent.ui.ui import (
    console, show_ok, show_info,
    show_err, show_warn, blank
)
from apex.agent.ui.dashboard import show_dashboard

load_dotenv()
show_dashboard()

last_response = ""
while True:
    blank()
    user_message = Prompt.ask("[bold cyan]>[/bold cyan]").strip()

    if not user_message:
        continue

    if user_message.lower() == "exit":
        show_info("Bye 👋")
        break

    
    if user_message.startswith("/save"):
        parts = user_message.split()
        if len(parts) < 2:
            show_err("Usage: /save <filename>")
            continue
        blocks = re.findall(r'```(?:\w+)?\n(.*?)```', last_response, re.DOTALL)
        if not blocks:
            show_err("No code found in last response.")
            continue
        for i, block in enumerate(blocks):
            name = parts[1] if i == 0 else f"{os.path.splitext(parts[1])[0]}_{i}{os.path.splitext(parts[1])[1]}"
            show_ok(write_file(name, block))
        continue

    
    if user_message.startswith("/index"):
        parts = user_message.split(maxsplit=1)
        if len(parts) < 2:
            show_err("Usage: /index <folder>")
            continue
        path = parts[1].strip()
        if not os.path.exists(path):
            show_err(f"Path not found: {path}")
            continue
        show_info("Indexing project …")
        import apex.rag.rag as rag_module
        result = rag_module.indexing(path)
        show_ok(f"RAG ready — {path}") if result else show_err("No code files found.")
        continue

    
    if user_message.startswith("/github"):
        handle_github(user_message[7:].strip())
        continue


    if user_message.startswith(("/WDhelp", "/wdhelp")):
        handle_watchdog("wdhelp"); continue
    if user_message.startswith("/analyze"):
        handle_watchdog(user_message[1:]); continue
    if user_message.startswith("/fix"):
        handle_watchdog(user_message[1:]); continue
    if user_message.startswith("/test"):
        handle_watchdog(user_message[1:]); continue
    if user_message.startswith("/watch"):
        handle_watchdog(user_message[1:]); continue
    if user_message.startswith("/wdstop"):
        handle_watchdog("wdstop"); continue

    
    if user_message.startswith("/help"):
        handle_help(); continue

    if user_message.startswith("/setting"):
        show_info(handle_settings(user_message.split()[1:]))
        continue

    
    if user_message.startswith("/auto"):
        parts = user_message.split()
        if len(parts) < 2:
            show_err("Usage: /auto on | /auto off")
            continue
        if parts[1] == "on":
            config["auto_mode"] = True;  save(); show_ok("Auto mode ON")
        elif parts[1] == "off":
            config["auto_mode"] = False; save(); show_ok("Auto mode OFF")
        continue

   
    if config.get("auto_mode"):
        run_auto(user_message)
        continue

    # normal — pass to agent
    last_response = run_agent(user_message)