import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from apex.agent.ui.ui import console, show_info, show_ok, show_warn, show_err, light_line, blank, BCY, CY, YEL, DIM
from apex.models.fallback import llm_safe
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil, os, tempfile, time, subprocess, threading
from apex.models.router import WATCHDOG_MODELS

_observer   = None
_watch_path = None
_fixing = False


def _read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        show_err(f"Cannot read file: {e}")
        return None


def ask_llm(prompt, max_token=500 , model_list = None):
    messages = [
        {"role": "system", "content": "You are a code reviewer. Be short and direct."},
        {"role": "user",   "content": prompt}
    ]
    r = llm_safe(messages, model_list = model_list , max_tokens=max_token)
    return r.choices[0].message.content or "" if r else "LLM unavailable."


def analyze(path):
    show_info(f"Analyzing {path} …")
    code = _read_file(path)
    if not code: return
    prompt = (
        f"Analyze this code file.\n"
        f"List ONLY real bugs and errors that will cause crashes or wrong results.\n"
        f"Ignore: missing docstrings, type hints, naming conventions, style issues.\n"
        f"Keep each point short. Max 5 points.\n\nFile: {path}\n\n{code[:2000]}"
    )
    result = ask_llm(prompt, max_token=400)
    console.print(Panel(result, title=f"[bold cyan]Analysis — {os.path.basename(path)}[/bold cyan]",
                        border_style=CY, padding=(1, 2)))
    light_line()


def fix(path):
    code = _read_file(path)
    if not code: return
    show_info(f"Fixing {path} …")
    global _fixing
    _fixing = True
    prompt = (
        f"Fix ONLY the broken functions in this code.\n"
        f"Do NOT change working functions.\n"
        f"If there is top-level code using input(), wrap it in 'if __name__ == \"__main__\":'.\n"
        f"Return the COMPLETE file with ALL functions, with only the broken parts fixed.\n"
        f"Return ONLY raw Python code. No explanation. No markdown. No text before or after.\n\n"
        f"File: {path}\n\n{code[:3000]}"
    )
    fixed_code = ask_llm(prompt, max_token=2400, model_list = WATCHDOG_MODELS)
    if "```" in fixed_code:
        fixed_code = fixed_code.split("```")[1]
        if fixed_code.startswith("python"):
            fixed_code = fixed_code[6:]
    fixed_code = fixed_code.strip()

    console.print(Panel(
        fixed_code[:1000] + ("\n… (truncated)" if len(fixed_code) > 1000 else ""),
        title="[bold yellow]● Preview[/bold yellow]", border_style=YEL, padding=(0, 2)
    ))

    confirm = input("  ● Overwrite file? (yes / no): ").strip().lower()
    if confirm != "yes":
        show_warn("Fix cancelled.")
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(fixed_code)
        show_ok(f"File fixed and saved: {path}")
    except Exception as e:
        show_err(f"Could not save: {e}")
    light_line()
    _fixing = False


def test(path):
    code = _read_file(path)
    if not code: return
    show_info(f"Generating tests for {path} …")
    prompt = (
        f"Write Python unit tests using unittest for this file.\n"
        f"Rules:\n"
        f"- Test ONLY the individual functions like add, subtract, multiply, divide.\n"
        f"- Do NOT test the main block or if __name__ == '__main__' section.\n"
        f"- Do NOT mock input() or print() unless the function itself calls them.\n"
        f"- Do NOT modify or add imports to the original file.\n"
        f"- Cover normal cases, edge cases, and errors.\n"
        f"Return ONLY the test code. No explanation.\n\nFile: {path}\n\n{code[:2500]}"
    )
    test_code = ask_llm(prompt, max_token=1300, model_list = WATCHDOG_MODELS)
    lines = test_code.strip().splitlines()
    if lines and lines[0].startswith("```"):  lines = lines[1:]
    if lines and lines[-1].strip() == "```":  lines = lines[:-1]
    test_code = "\n".join(lines)

    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(path, os.path.join(tmp, os.path.basename(path)))
        test_file = os.path.join(tmp, "test_apex.py")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_code)
        show_info("Running tests in safe environment …")
        try:
            result = subprocess.run(
                ["python", "-m", "unittest", "test_apex", "-v"],
                cwd=tmp, capture_output=True, text=True, timeout=10
            )
            output = result.stderr + result.stdout
        except subprocess.TimeoutExpired:
            show_err("Tests timed out after 10 seconds."); return
        except Exception as e:
            show_err(f"Could not run tests: {e}"); return

    passed = "OK" in output
    color  = YEL if passed else "red"
    title  = "[bold yellow]● Tests Passed[/bold yellow]" if passed else "[bold red]● Tests Failed[/bold red]"
    console.print(Panel(output[-1500:], title=title, border_style=color))
    if not passed:
        show_warn(f"Run /fix {path} to fix the issues.")
    light_line()


class _ApexHandler(FileSystemEventHandler):
    def __init__(self, target_path):
        self.target_path = os.path.abspath(target_path)
        self.last_trigger = 0

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == self.target_path:
            now = time.time()
            if now - self.last_trigger < 5: return
            self.last_trigger = now
            t = Text()
            t.append("\n  ● ", style=CY)
            t.append(f"Change detected — {os.path.basename(self.target_path)}", style=BCY)
            console.print(t)
            if _fixing: return
            analyze(self.target_path)


def watch(path):
    global _observer, _watch_path
    if not os.path.exists(path):
        show_err(f"File not found: {path}"); return
    if _observer and _observer.is_alive():
        show_warn(f"Already watching: {_watch_path} — stop it first with /wdstop"); return
    _watch_path = path
    folder  = os.path.dirname(os.path.abspath(path)) or "."
    handler = _ApexHandler(path)
    _observer = Observer()
    _observer.schedule(handler, folder, recursive=False)
    _observer.start()
    show_ok(f"Watching: {path}")


def watch_stop():
    global _observer, _watch_path
    if not _observer or not _observer.is_alive():
        show_warn("No active watch."); return
    _observer.stop(); _observer.join()
    _observer = _watch_path = None
    show_info("Watch stopped.")


def watchdog_guide():
    t = Table(title="APEX — Watchdog Commands", border_style=CY,
              header_style=BCY, box=box.SIMPLE_HEAVY, show_lines=False)
    t.add_column("Command",      style="bold yellow", no_wrap=True)
    t.add_column("What it does", style="white")
    t.add_row("/analyze <file>", "Scan a file — list bugs, bad practices, missing error handling")
    t.add_row("/fix <file>",     "Auto-fix all issues. Shows preview before overwriting")
    t.add_row("/test <file>",    "Generate unit tests and run in a safe sandbox")
    t.add_row("/watch <file>",   "Watch a file — auto-analyze on every save")
    t.add_row("/wdstop",         "Stop the active file watcher")
    t.add_row("/WDhelp",         "Show this help menu")
    console.print(t)


def handle_watchdog(command):
    parts = command.strip().split()
    if not parts: watchdog_guide(); return
    cmd = parts[0].lower()
    if   cmd == "analyze": analyze(parts[1]) if len(parts) > 1 else show_err("Usage: /analyze <file>")
    elif cmd == "fix":     fix(parts[1])     if len(parts) > 1 else show_err("Usage: /fix <file>")
    elif cmd == "test":    test(parts[1])    if len(parts) > 1 else show_err("Usage: /test <file>")
    elif cmd == "watch":   watch(parts[1])   if len(parts) > 1 else show_err("Usage: /watch <file>")
    elif cmd == "wdstop":  watch_stop()
    elif cmd == "wdhelp":  watchdog_guide()
    else: show_err(f"Unknown watchdog command: {parts[0]} — try /WDhelp")