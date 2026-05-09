import os 
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rich.console import Console

console = Console()

C = "#A1E3F9"  # custom color for /commands


def show_help():
    console.print()
    console.print("[bold cyan]APEX ⚡ — Help Guide[/bold cyan]")
    console.print()

    console.print("[bold white]── Core Commands ──[/bold white]")
    console.print("  exit                              Quit APEX")
    console.print(f"  [{C}]/help[/{C}]                             Show this help menu")
    console.print(f"  [{C}]/save[/{C}] [bold white]<filename>[/bold white]                  Save last code block to a file")
    console.print(f"  [{C}]/index[/{C}] [bold white]<folder>[/bold white]                   Index a project folder for code search (RAG)")
    console.print(f" [{C}] /setting[/{C}]                          can edit keys -> update, delete")
    console.print(f" [{C}] /auto on [/{C}]                         use this command to automate the tools")
    console.print(f" [{C}] /auto off[/{C}]                         use this command to off this mode ")
    console.print()

    console.print("[bold white]── Setting (/setting ...) ──[/bold white]")
    console.print(f"[{C}] /setting show [/{C}]          show's all info about keys, indent level")
    console.print(f"[{C}] /setting <set> <value> [/{C}] can update the key and indent level")
    console.print(f"[{C}] /setting delete <set>  [/{C}] you can delete your api key")
    console.print(f" → Example (/setting <set> <value>) : [{C}] /setting [/{C}] google_api_key absc***************")
    console.print(f" → Example (/setting <set> <value>) : [{C}] /setting [/{C}] Beginner Intermediate")
    console.print(f" → Example (/setting delete <set>)  : [{C}] /setting delete[/{C}] google_api_key ")
    console.print()


    console.print("[bold white]── GitHub (/github ...) ──[/bold white]")
    console.print("  How to get a GitHub token:")
    console.print("    1. Go to [link]https://github.com/settings/tokens[/link]")
    console.print("    2. Click 'Generate new token' → choose 'Tokens (classic)'")
    console.print(f"  [{C}]/github[/{C}] login [bold white]<token>[/bold white]             Save your GitHub token")
    console.print(f"    → Example: [{C}]/github[/{C}] login ghp_xxxxxxxxxxxx")
    console.print(f"  [{C}]/github[/{C}] list                      List your repositories")
    console.print(f"  [{C}]/github[/{C}] search [bold white]<keyword>[/bold white]          Search public repos")
    console.print(f"  [{C}]/github[/{C}] commits [bold white]<owner/repo>[/bold white]      Show last 5 commits")
    console.print(f"  [{C}]/github[/{C}] make [bold white]<repo-name>[/bold white]          Create a new repo")
    console.print(f"  [{C}]/github[/{C}] push [bold white]<owner/repo> <file> <msg>[/bold white]   Upload a file")
    console.print(f"  [{C}]/github[/{C}] pull [bold white]<owner/repo> <file>[/bold white]  Download a file")
    console.print(f"  [{C}]/github[/{C}] view [bold white]<owner/repo> <file>[/bold white]  Preview a file with syntax highlight")
    console.print(f"  [{C}]/github[/{C}] help                      GitHub-specific help")
    console.print()

    console.print("[bold white]── Watchdog & Code Quality ──[/bold white]")
    console.print(f"  [{C}]/analyze[/{C}] [bold white]<file>[/bold white]                   Scan file for bugs and bad practices")
    console.print(f"  [{C}]/fix[/{C}] [bold white]<file>[/bold white]                       Auto-fix issues in a file (asks before saving)")
    console.print(f"  [{C}]/test[/{C}] [bold white]<file>[/bold white]                      Generate and run unit tests in a sandbox")
    console.print(f"  [{C}]/watch[/{C}] [bold white]<file>[/bold white]                     Watch a file, auto-analyze on every save")
    console.print(f"  [{C}]/wdstop[/{C}]                           Stop the active file watcher")
    console.print(f"  [{C}]/WDhelp[/{C}]                           Watchdog-specific help")
    console.print()

    console.print("[bold white]── RAG — Project Code Search ──[/bold white]")
    console.print(f"  1. Run [{C}]/index[/{C}] [bold white]<folder>[/bold white] to index your project")
    console.print(f"  2. Then ask naturally: [{C}]'where is the login function?'[/{C}] or [{C}]'find the auth logic'[/{C}]")
    console.print("  Supported: .py .js .ts .java .cpp .c .cs .kt .scala .html .md")
    console.print()

    console.print("[bold white]── Tips ──[/bold white]")
    console.print("  - Mention 'beginner' / 'intermediate' / 'advanced' to adjust response depth")
    console.print(f"  - Use [{C}]/save[/{C}] right after APEX writes code to save it to disk")
    console.print("  - Use words like 'secure', 'JWT', 'hash' to switch to security mode")
    console.print("  - Use words like 'algorithm', 'big O', 'leetcode' for DSA mode with complexity analysis")
    console.print("  - Use 'build a full', 'from scratch', 'entire project' to unlock higher token budget")
    console.print()

    console.print("[dim]  Type your question or command and press Enter.[/dim]")
    console.print(f"  [dim]For more on a specific area: [{C}]/github[/{C}] help | [{C}]/WDhelp[/{C}][/dim]")
    console.print()


def handle_help(args: str = ""):
    show_help()