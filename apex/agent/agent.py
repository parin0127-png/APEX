import os
from apex.agent.planner import plan
from apex.config.system import is_chat, build_prompt, get_max_tokens, build_chat_prompt
from apex.models.fallback import llm_safe
from apex.models.router import MODELS, CHAT_MODELS
from apex.tools.tools import REGISTRY
from apex.agent.ui.ui import (
    show_response, show_thinking, show_tokens,
    show_tool_call, show_info, show_warn,
    show_err, light_line
)

MAX_STEPS = 5
history = []

def get_history():
    clean = [m for m in history if m["role"] in ("user" , "assistant")]
    return clean[-4:]

def _get_args(tool_name : str, user_message : str):
    prompts = {
        "run_cmd"            : "Return ONLY the terminal command. No explanation.",
        "find_relevant_code" : "Return ONLY 2-4 word search query. No explanation.",
        "read_file"          : "Return ONLY the file path. No explanation.",
        "fix_code"           : "Return ONLY the file path to fix. No explanation.",
        "delete_file"        : "Return ONLY the file path to delete. No explanation.",
        "list_dir"           : "Return ONLY the folder path. No explanation.",
    }

    messages = [
        {"role" : "system" , "content" : prompts.get(tool_name, "Return only the argument.")},
        {"role" : "user" , "content" : user_message}
    ]

    response = llm_safe(
        messages,
        model_list = CHAT_MODELS,
        max_tokens = 40
    )
    if response is None:
        return user_message
    return response.choices[0].message.content.strip()

def run_tool(tool_name : str, user_message : str, context : str):
    func = REGISTRY.get(tool_name)
    if func is None:
        return f"Unknown tool: {tool_name}"

    arg = _get_args(tool_name, user_message)
    show_info(f"  arg → {arg}")

    if tool_name == "fix_code":
        error = context[-200:] if context else "fix all issues"
        return func(arg , error)

    return func(arg)

def run_agent(user_message : str):
    global history

    chat = is_chat(user_message)
    max_tok = get_max_tokens(user_message , chat)
    model_list = CHAT_MODELS if chat else MODELS
    context = ""

    if not chat:
        for _ in range(MAX_STEPS):
            tool_name = plan(user_message)
            show_info(f"plan → {tool_name}")

            if tool_name in ("answer" , "write_file"):
                break

            show_tool_call(tool_name)
            result = run_tool(tool_name, user_message, context)

            if result == "NO_RAG":
                show_warn("No project loaded — use /index <folder> first.")
                context = "\n No project indexed."
                break

            context += f"\n[{tool_name}]: {str(result)[:1500]}"

            if not str(result).lower().startswith("error"): 
                break
    return answer(user_message, context, model_list, max_tok, chat = chat)

def answer(user_message: str, context: str, model_list: list, max_tok: int, chat = False) -> str:
    global history

    
    content  = f"{user_message}\n\nContext:\n{context}" if context.strip() else user_message
    prompt = build_chat_prompt() if chat else build_prompt()
    messages = [{"role": "system", "content": build_prompt()}]
    messages += get_history()
    messages.append({"role": "user", "content": content})

    current_model = model_list[0]["model"]
    show_thinking(current_model)

    response = llm_safe(messages, model_list=model_list, max_tokens=max_tok)

    if response is None:
        show_err("All models failed. Try again.")
        return ""

    text = response.choices[0].message.content or ""

    if text:
        show_response(text, model=current_model)
        show_tokens(response.usage.total_tokens)

        history.append({"role": "user",      "content": user_message})
        history.append({"role": "assistant",  "content": text})

        if len(history) > 8:
            history = history[-8:]

    light_line()
    return text