import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from rich.console import Console
from apex.models.fallback import llm_safe
from apex.models.router import AUTO_CHAT_MODELS
from apex.tools.tools import REGISTRY
from apex.auto.stages import stage_run_cmd, stage_write_file, stage_read_file, stage_fix_code
from apex.auto.memory import save_memory, summarize_memory
from apex.agent.ui.ui import (
    show_info, show_warn, show_ok, show_err,
    show_mode_auto, show_pipeline_step, show_pipeline_done, light_line, blank
)

console = Console()

AUTO_TOOLS = ["run_cmd", "write_file", "read_file", "fix_code", "done"]

STAGES = {
    "run_cmd":    stage_run_cmd,
    "write_file": stage_write_file,
    "read_file":  stage_read_file,
    "fix_code":   stage_fix_code,
}


def small_divider():
    console.print("[dim]" + "─" * 90 + "[/dim]")


def router(goal, last_result, past=""):

    # small circle + apex thinking
    console.print("[bright_blue]◉[/bright_blue] [white]APEX thinking....[/white]")

    system_prompt = """
        Router agent. Pick next tool only.
        Rules:
        1. writing/creating code → write_file
        2. file written → run_cmd
        3. run_cmd has Error/Traceback/Exception → fix_code
        4. fix_code done → run_cmd
        5. done → done
        Reply ONLY: {"tool": "tool_name"}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Past content:\n{past}\nGoal: {goal}\nHistory:\n{last_result}\nWhat tool next?"
        }
    ]

    response = llm_safe(
        messages,
        model_list=AUTO_CHAT_MODELS,
        max_tokens=20,
    )

    text = response.choices[0].message.content

    try:
        return json.loads(text)["tool"]

    except:
        show_warn("Router failed to parse — defaulting to done")
        return "done"


def run_auto(goal):

    show_mode_auto(goal)

    last_result = "No result yet"
    MAX_STEPS   = 10
    steps       = 0
    history     = []

    while True:

        # dim line before every APEX thinking
        small_divider()

        if steps >= MAX_STEPS:
            show_warn("Max steps reached — stopping.")
            save_memory(goal, last_result)
            break

        tool_name = router(
            goal,
            "\n".join(history[-2:]) if history else "No result yet"
        )

        if tool_name == "done":
            show_pipeline_done(last_result)
            save_memory(goal, last_result)
            break

        if tool_name not in STAGES:
            show_err(f"Unknown tool: {tool_name} — stopping.")
            break

        last_result = STAGES[tool_name](goal, last_result)

        show_pipeline_step(steps + 1, tool_name, last_result)

        error_kw = [
            "error",
            "traceback",
            "exception",
            "syntaxerror",
            "nameerror",
            "typeerror"
        ]

        if tool_name == "run_cmd":

            if not any(k in last_result.lower() for k in error_kw):

                show_ok("Output received — task complete.")
                save_memory(goal, last_result)
                show_pipeline_done(last_result)
                break

        if "Server started in background" in last_result:
            show_ok("Server running — task complete.")
            save_memory(goal, last_result)
            show_pipeline_done(last_result)
            break

        history.append(
            f"Step {steps + 1}: {tool_name} → {last_result[:100]}"
        )

        steps += 1