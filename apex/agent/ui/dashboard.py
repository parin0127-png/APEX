import os
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import platform
import unicodedata
from rich.console import Console
from rich.text import Text

console = Console()
OS = platform.system()


def vlen(s: str) -> int:
    count = 0
    for c in s:
        ea = unicodedata.east_asian_width(c)
        count += 2 if ea in ("W", "F") else 1
    return count


def rpad(s: str, width: int) -> str:
    return s + " " * max(0, width - vlen(s))


def show_dashboard():
    INNER = 118
    LEFT  = 52
    RIGHT = INNER - LEFT - 1

    B = "white"
    C = "bright_cyan"

    # APEX art shifted more to center of left panel
    A = "        "   # 8 spaces indent for APEX ASCII art
    # other left content stays at 3 spaces
    L = "   "
    # right panel indent
    P = "            "

    left_lines = [
        "",
        f"{A}██████╗ ██████╗ ███████╗██╗  ██╗",
        f"{A}██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝",
        f"{A}███████║██████╔╝█████╗   ╚███╔╝ ",
        f"{A}██╔══██║██╔═══╝ ██╔══╝   ██╔██╗ ",
        f"{A}██║  ██║██║     ███████╗██╔╝ ██╗",
        f"{A}╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝",
        "",
        f"{L}⚡ Your Coding Assistant",
        f"{L}{OS} | {platform.release()}",
        f"{L}{os.getcwd()}",
        "",
        f"{L}Powered by",
        f"{L}⚡ Groq     fast inference",
        f"{L}🌀 Mistral  automation",
        "",
    ]

    right_lines = [
        "",
        f"{P}Commands",
        "",
        f"{P}/index  <path>   load project for RAG",
        f"{P}/save   <file>   save last code",
        f"{P}/github          github actions",
        f"{P}/watch <path>    monitor's code",
        f"{P}/auto on         Automate tools",
        f"{P}exit             quit APEX",
        "",
        f"{P}... /help for more",
        "",
        f"{P}Features",
        "",
        f"{P}📁 RAG                 search your project",
        f"{P}🔧 Tools               run commands safely",
        f"{P}🐙 GitHub              manage your repos",
        f"{P}💾 Save                save code with /save",
        f"{P}👀 Watchdog            monitor your code /watch",
        f"{P}🧠 Smart Automation    Automate Tools"
        "",
    ]

    rows = max(len(left_lines), len(right_lines))
    left_lines  += [""] * (rows - len(left_lines))
    right_lines += [""] * (rows - len(right_lines))

    title  = " APEX v1.0 "
    side   = (INNER - len(title)) // 2
    extra  = (INNER - len(title)) - side * 2
    top    = "+" + "-" * side + title + "-" * (side + extra) + "+"
    bottom = "+" + "-" * INNER + "+"

    console.print(Text(top, style=B))

    for l, r in zip(left_lines, right_lines):
        lc  = rpad(l, LEFT)
        rc  = rpad(r, RIGHT)
        row = Text()
        row.append("|",  style=B)
        row.append(lc,   style=C)
        row.append("|",  style=B)
        row.append(rc,   style=C)
        row.append("|",  style=B)
        console.print(row)

    console.print(Text(bottom, style=B))
    console.print()


if __name__ == "__main__":
    show_dashboard()
    while True:
        try:
            user_input = console.input("[bright_cyan]You:[/bright_cyan] ")
            if user_input.strip().lower() == "exit":
                console.print("[dim]Goodbye.[/dim]")
                break
        except (KeyboardInterrupt, EOFError):
            break