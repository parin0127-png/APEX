import os 
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from groq import Groq
from openai import OpenAI
from apex.tools.tools import REGISTRY
from dotenv import load_dotenv
from apex.config.settings import config
from apex.models.router import MISTRAL_MODEL_NAMES, MODELS
import logging
import time

load_dotenv()
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def get_client(model: str):
    m = model.lower()
    if any(name == m for name in MISTRAL_MODEL_NAMES):
        # print(f"→ Routing {model} to Mistral")
        return OpenAI(
            api_key  = config.get("mistral_api_key"),
            base_url = "https://api.mistral.ai/v1"
        )
    # print(f"→ Routing {model} to Groq")
    return Groq(api_key=config.get("api_key"))

def _trim_messages(messages: list) -> list:
    system     = [m for m in messages if m["role"] == "system"]
    non_system = [m for m in messages if m["role"] != "system"]
    recent     = non_system[-6:]

    trimmed = []
    for m in recent:
        if m["role"] == "assistant" and m.get("content") and len(m["content"]) > 600:
            copy            = dict(m)
            copy["content"] = m["content"][:500] + "\n... trimmed to save space"
            trimmed.append(copy)
        else:
            trimmed.append(m)

    result = system + trimmed  
    # print(f"⚠ Messages trimmed: {len(messages)} → {len(result)}")
    return result              


def _try_models(messages: list, label: str, color: str, model_list: list, max_tokens: int = 2500):

    for cfg in model_list:
        model           = cfg["model"]
        current_message = messages
        client          = get_client(model)
        retry           = 0

        while retry < 3:
            try:
                kwargs = {
                    "model"     : model,
                    "messages"  : current_message,
                    "max_tokens": max_tokens,
                }
                if retry == 0:
                    print(f"{label}...")
                response = client.chat.completions.create(**kwargs)
                print(f"✔ [{model}] Tokens: {response.usage.total_tokens}")
                return response

            except Exception as e:
                error_msg = str(e).lower()
                # print(f"FULL ERROR: {e}")

                if "413" in error_msg or "payload" in error_msg:
                    current_message = _trim_messages(current_message)
                    retry += 1

                elif "429" in error_msg or "rate_limit" in error_msg:
                    if "per_minute" in error_msg or "tpm" in error_msg:
                        # print(f"! [{model}] RPM hit — waiting 5s...")
                        time.sleep(5)
                        retry += 1
                    else:
                        # print(f"! [{model}] TPD exhausted — next model...")
                        break

                elif "400" in error_msg or "tools" in error_msg:
                    # print(f   "! [{model}] Tool error — retrying without tools...")
                    try:
                        response = client.chat.completions.create(
                            model      = model,
                            messages   = current_message,
                            max_tokens = max_tokens,
                        )
                        # print(f"✔ [{model}] (no tools) Tokens: {response.usage.total_tokens}")
                        return response
                    except Exception as e1:
                        print(f"! [{model}] Failed: {e1}")
                        break
                else:
                    print(f"! [{model}] Error: {e}")
                    break

    return None


def llm_safe(messages: list, model_list: list = None, max_tokens: int = 2500):
    primary  = model_list or MODELS
    response = _try_models(messages, "APEX thinking...", "yellow", primary, max_tokens)
    if response:
        return response