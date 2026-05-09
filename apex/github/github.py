import os 
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint
from apex.config.settings import config,CONFIG_PATH
import requests
import json
import base64

console = Console()

GITHUB_TOKEN = config.get("github_token" , "")

config["github_token"] = GITHUB_TOKEN

c = "#A1E3F9"

def github_login(token):
    global GITHUB_TOKEN                    
    GITHUB_TOKEN = token
    config["github_token"] = token
    with open(CONFIG_PATH, "w") as f:       
        json.dump(config, f, indent=4)
    console.print(Panel("[bold green]✅ Token saved! You are now connected to GitHub.[/bold green]", title="GitHub Login", border_style="green"))

def call_github(url , params = None):
    headers = {"Authorization": f"token  {GITHUB_TOKEN}"}
    response = requests.get(url , headers = headers, params = params)
    if response.status_code == 401:
        rprint("[bold red]❌ Wrong token. Use /github login <your_token>[/bold red]")
        return None
    if not response.ok:
        rprint(f"[bold red]❌ Error: {response.json().get('message', 'something went wrong')}[/bold red]")
        return None
    return response.json()

    

def search_repo(keyword):
    console.print(f"\n[bold cyan]🔍 Searching repos for:[/bold cyan] [yellow]{keyword}[/yellow]\n")
    data = call_github("https://api.github.com/search/repositories",params = {"q" : keyword, "per_page" : 5})
    if data:
        table = Table(title="Search Results", border_style="cyan", header_style="blue")
        table.add_column("Repo",        style = "bold white")
        table.add_column("⭐ Stars" , style = "yellow" , justify = "right")
        table.add_column("Description" , style = "dim white")

        for repo in data["items"]:
            table.add_row(
                repo["full_name"],
                str(repo["stargazers_count"]),
                repo.get("description") or "No description"
            )
        
        console.print(table)

def list_repo():
    data = call_github("https://api.github.com/user/repos", params={"per_page": 10, "sort": "updated"})
    if data:
        table = Table(title="Your Repositories", border_style="blue", header_style="blue")
        table.add_column("Visibility" , justify = "center")
        table.add_column("Name" , style = "bold white")
        table.add_column("Description" , style = "dim white")

        for repo in data:
            lock = "[red]🔒 Private[/red]" if repo["private"] else "[green]🌍 Public[/green]"
            table.add_row(lock, repo["name"], repo.get("description") or "No description")
        
        console.print(table)

def view_commits(repo_name):
    data = call_github(f"https://api.github.com/repos/{repo_name}/commits", params = {"per_page" : 5})
    if data :
        table = Table(title = f"Last 5 commits -> {repo_name}" , border_style = "yellow", header_style = "bold megenta")
        table.add_column("SHA" , style = "cyan", width = 8)
        table.add_column("Date" , style = "dim white" , width = 12)
        table.add_column("Author" , style = "green")
        table.add_column("Message" , style = "white")

        for commit in data:
            table.add_row(
                commit["sha"][:7],
                commit["commit"]["author"]["date"][:10],
                commit["commit"]["author"]["name"],
                commit["commit"]["message"].split("\n")[0]
            )

        console.print(table)

def make_repo(repo_name):
    headers = {"Authorization": f"token  {GITHUB_TOKEN}", "Accept" : "application/vnd.github+json"}
    body = {"name" : repo_name, "auto_init" : True, "private" : False}
    response = requests.post("https://api.github.com/user/repos", headers = headers, json = body)

    if response.ok:
        data = response.json()
        console.print(Panel(
            f"[bold white]Name  :[/bold white] [cyan]{data['full_name']}[/cyan]\n"
            f"[bold white]Link  :[/bold white] [blue underline]{data['html_url']}[/blue underline]\n"
            f"[bold white]Clone :[/bold white] [yellow]git clone {data['clone_url']}[/yellow]",
            title="[bold green] Repo Created![/bold green]",
            border_style="green"
        ))

    else:
        rprint(f"[bold red]❌ Could not create repo: {response.json().get('message')}[/bold red]")

def push_file(repo_name, file_path , commit_message):
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        rprint(f"[bold red]❌ File not found: {file_path}[/bold red]")
        return
    
    file_name = file_path.split("/")[-1]
    encoded = base64.b64encode(content.encode()).decode()
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept" : "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_name}"

    existing = requests.get(url, headers = headers)
    sha =   existing.get("sha")
    body = {"message" : commit_message , "content" : encoded}

    sha = None
    if existing.status_code == 200:
        sha = existing.json().get("sha")

    with console.status(f"[cyan]Pushing {file_name}...[/cyan]"):
        response = requests.put(url , headers = headers, json = body)
    
    if response.ok:
        console.print(Panel(
            f"[bold white]File   :[/bold white] [cyan]{file_name}[/cyan]\n"
            f"[bold white]Repo   :[/bold white] [yellow]{repo_name}[/yellow]\n"
            f"[bold white]Commit :[/bold white] {commit_message}",
            title="[bold green]✅ Push Successful![/bold green]",
            border_style="green"
        ))
    else : 
        rprint(f"[bold red]❌ Push failed: {response.json().get('message')}[/bold red]")


def pull_repo(repo_name, file_name):
    with console.status(f"[cyan]Pulling {file_name}...[/cyan]"):
        data = call_github(f"https://api.github.com/repos/{repo_name}/contents/{file_name}")

    if data and "content" in data:
        content = base64.b64encode(data["content"]).decode("utf-8")

        with open(file_name, "w")as f:
            f.write(content)

        console.print(Panel(
            f"[bold white]File  :[/bold white] [cyan]{file_name}[/cyan]\n"
            f"[bold white]Saved :[/bold white] [green]Saved to your local folder ✅[/green]",
            title="[bold green]✅ Pull Successful![/bold green]",
            border_style="green"
        ))
    else:
        rprint(f"[bold red]❌ Could not find '{file_name}' in {repo_name}[/bold red]")

def view_file(repo_name, file_name):
    data = call_github(f"https://api.github.com/repos/{repo_name}/contents/{file_name}")

    if data and "content" in data:
        content = base64.b64encode(data["content"]).decode("utf-8")
        language = file_name.split(".")[-1]
        syntax   = Syntax(content[:3000], language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"[bold cyan]📄 {file_name} — {repo_name}[/bold cyan]", border_style="cyan"))

    else : 
        rprint(f"[bold red]❌ File not found in {repo_name}[/bold red]")


def show_help():
    table = Table(title="APEX — GitHub Commands", border_style="white", header_style="bold cyan", show_lines=True)
    table.add_column("Command",     style="bold yellow", no_wrap=True)
    table.add_column("What it does", style="white")
 
    table.add_row(f"[{c}]/github login [token] [/{c}]",                     "Save your GitHub token")
    table.add_row(f"[{c}]/github search [keyword] [/{c}]",                  "Search public repos")
    table.add_row(f"[{c}]/github list [/{c}]",                              "List your repos")
    table.add_row(f"[{c}]/github commits [owner/repo] [/{c}]",              "Show last 5 commits")
    table.add_row(f"[{c}]/github make [repo-name] [/{c}]",                  "Create a new repo")
    table.add_row(f"[{c}]/github push [owner/repo] [file] [msg] [/{c}]",   "Upload a file to repo")
    table.add_row(f"[{c}]/github pull [owner/repo] [file][/{c}]",         "Download a file from repo")
    table.add_row(f"[{c}]/github view [owner/repo] [file][/{c}]",         "Read a file with syntax highlight")
    table.add_row(f"[{c}]/github help[/{c}]",                              "Show this menu")

    console.print(table)

def handle_github(command):
    parts = command.strip().split()

    if not parts or parts[0] == "help":
        show_help()

    elif parts[0] == "login":
        if len(parts) < 2:
            rprint("[red]Token missing[/red]")
        else:
            github_login(parts[1])
        return
    elif parts[0] == "search":
        keyword = " ".join(parts[1:])
        search_repo(keyword)
    elif parts[0] == "list":
        list_repo()
    elif parts[0] == "commits":
        view_commits(parts[1])
    elif parts[0] == "make":
        make_repo(parts[1])
    elif parts[0] == "push":
        push_file(parts[1], parts[2], " ".join(parts[3:]))
    elif parts[0] == "pull":
        pull_repo(parts[1], parts[2])
    elif parts[0] == "view":
        if len(parts) < 3:
            rprint("[red]Usage: /github view [owner/repo] [file][/red]")
        else:
            view_file(parts[1] , parts[2])

    else : 
        rprint(f"[bold red]❓ Unknown command '[yellow]{parts[0]}[/yellow]'. Type /github help[/bold red]")