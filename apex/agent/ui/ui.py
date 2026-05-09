import os
import platform
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule
from rich.table import Table
from rich import box

console = Console()
OS = platform.system()

CY  = "cyan"
BCY = "bold cyan"
DIM = "dim"
YEL = "yellow"
ORA = "dark_orange"
WHT = "white"

def _dot(color=CY) -> Text:
    t = Text(); t.append("● ", style=color); return t

def blank():          console.print()
def light_line():     console.print(Rule(style=DIM))
def rule(title=""):   console.print(Rule(title=title, style=CY))

def show_ok(msg):
    t = Text(); t.append("  ● ", style=YEL); t.append(msg, style=WHT); console.print(t)

def show_info(msg):
    t = Text(); t.append("  ● ", style=CY);  t.append(msg, style=WHT); console.print(t)

def show_warn(msg):
    t = Text(); t.append("  ● ", style=ORA); t.append(msg, style=WHT); console.print(t)

def show_err(msg):
    t = Text(); t.append("  ● ", style="red"); t.append(msg, style=WHT); console.print(t)

def show_thinking(model=""):
    t = Text()
    t.append("  ● ", style=DIM)
    t.append("thinking", style=DIM)
    if model: t.append(f"  [{model}]", style=DIM)
    t.append(" …", style=DIM)
    console.print(t)

def show_tokens(n: int):
    t = Text(); t.append("  ● ", style=DIM); t.append(f"{n} tokens", style=DIM); console.print(t)

def show_tool_call(name: str):
    t = Text()
    t.append("  ● ", style=CY)
    t.append("tool  ", style=DIM)
    t.append(name, style=BCY)
    console.print(t)

def show_response(content: str, model: str = ""):
    subtitle = f"[dim]{model}[/dim]" if model else ""
    console.print(Panel(Markdown(content), title="[bold cyan]APEX ⚡[/bold cyan]",
                        subtitle=subtitle, border_style=CY, padding=(1, 2)))

def show_mode_auto(goal: str):
    blank()
    console.print(Rule(title=f"[bold cyan]AUTO[/bold cyan]  [dim]{goal[:60]}[/dim]", style=CY))

def show_mode_rag():
    t = Text()
    t.append("  ● ", style=CY); t.append("RAG  ", style=BCY); t.append("searching project …", style=DIM)
    console.print(t)

def show_mode_security():
    t = Text()
    t.append("  ● ", style=ORA); t.append("SECURITY", style="bold dark_orange")
    t.append("  OWASP mode active", style=DIM)
    console.print(t); blank()

def show_mode_dsa():
    t = Text()
    t.append("  ● ", style=CY); t.append("DSA", style=BCY)
    t.append("  complexity analysis on", style=DIM)
    console.print(t); blank()

def show_pipeline_step(n: int, tool: str, result: str = ""):
    t = Text()
    t.append(f"  {n}  ", style=DIM); t.append("● ", style=CY); t.append(f"{tool:<14}", style=BCY)
    if result:
        short = result.strip().splitlines()[0][:60]
        t.append(short, style=DIM)
    console.print(t)

def show_pipeline_done(result: str):
    blank()
    console.print(Panel(Text(result[:400], style=WHT), title="[bold yellow]● done[/bold yellow]",
                        border_style=YEL, padding=(0, 2)))
    light_line(); blank()

def make_table(title: str, columns: list, rows: list) -> Table:
    t = Table(title=title, border_style=CY, header_style=BCY,
              box=box.SIMPLE_HEAVY, show_lines=False)
    for col, style in columns:
        t.add_column(col, style=style)
    for row in rows:
        t.add_row(*row)
    return t

def show_dashboard():
    blank()
    logo_lines = [
        "   ██████╗ ██████╗ ███████╗██╗  ██╗",
        "   ██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝",
        "   ███████║██████╔╝█████╗   ╚███╔╝ ",
        "   ██╔══██║██╔═══╝ ██╔══╝   ██╔██╗ ",
        "   ██║  ██║██║     ███████╗██╔╝ ██╗",
        "   ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝",
    ]
    for line in logo_lines:
        console.print(Text(line, style=BCY))
    console.print(Text("   ⚡  Your Coding Assistant  —  v1.0", style=DIM))
    blank(); console.print(Rule(style=CY))

    sys_line = Text()
    sys_line.append("  ● ", style=CY); sys_line.append(f"{OS} {platform.release()}", style=WHT)
    sys_line.append("   ● ", style=CY); sys_line.append(os.getcwd(), style=DIM)
    console.print(sys_line)

    inf_line = Text()
    inf_line.append("  ● ", style=CY); inf_line.append("Groq  ", style=WHT); inf_line.append("fast inference", style=DIM)
    inf_line.append("   ● ", style=CY); inf_line.append("Mistral  ", style=WHT); inf_line.append("fallback", style=DIM)
    console.print(inf_line)
    console.print(Rule(style=CY)); blank()

    cmds = [
        ("/index  <path>",  "load project for RAG"),
        ("/save   <file>",  "save last code block"),
        ("/github",         "github actions"),
        ("/watch  <path>",  "monitor code changes"),
        ("/auto   on|off",  "toggle auto mode"),
        ("/help",           "full help guide"),
        ("exit",            "quit APEX"),
    ]
    cmd_text = Text()
    for cmd, desc in cmds:
        cmd_text.append("  ● ", style=CY)
        cmd_text.append(f"{cmd:<20}", style=BCY)
        cmd_text.append(f"{desc}\n", style=DIM)
    console.print(Panel(cmd_text, title="[bold cyan]Commands[/bold cyan]",
                        border_style=CY, padding=(0, 2)))
    blank(); console.print(Rule(style=DIM)); blank()