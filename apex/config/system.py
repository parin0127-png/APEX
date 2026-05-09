import os
import platform

OS  = platform.system()
CWD = os.getcwd()

WORK_KEYWORDS = [
    "write", "create", "build", "make", "fix", "debug", "refactor",
    "run", "execute", "install", "find", "search", "locate", "explain",
    "optimize", "implement", "generate", "develop", "analyze", "test",
    "where is", "how does", "show me", "read", "open", "check",
    ".py", ".js", ".ts", ".java", ".cpp", ".html", ".go", ".rs",
]

PROJECT_KEYWORDS = [
    "full project", "entire project", "from scratch", "full stack",
    "build a", "create a", "web app", "rest api", "cli tool",
    "with database", "with auth", "production ready",
]

def is_chat(message: str) -> bool:
    msg = message.lower().strip()
    return not any(k in msg for k in WORK_KEYWORDS)

def is_project(message: str) -> bool:
    msg = message.lower().strip()
    return any(k in msg for k in PROJECT_KEYWORDS)

def get_max_tokens(message: str, chat: bool) -> int:
    if chat:
        return 150
    if is_project(message):
        return 6000
    return 2500

def build_chat_prompt() -> str:
    return "You are APEX, a coding assistant. Be very brief."

def build_prompt() -> str:
    return (
        f"You are APEX, a senior coding assistant. "
        f"OS: {OS} {platform.release()}. CWD: {CWD}. "
        f"Be direct and short. Use tools only when needed."
        f"If context is provided, answer ONLY from it. If answer is not in context, say 'Not found in project'."
    )