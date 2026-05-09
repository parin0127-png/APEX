MODELS = [
    {"provider": "groq", "model": "llama-3.1-8b-instant"},
    {"provider": "groq", "model": "llama-3.3-70b-versatile"},
    {"provider": "groq", "model": "openai/gpt-oss-120b"},
]

CHAT_MODELS = [
    {"provider": "groq", "model": "llama-3.1-8b-instant"},
    {"provider": "groq", "model": "groq/compound-mini"},
]

HEAVY_TOOLS = {
    "run_cmd": [
        {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        {"provider": "mistral", "model": "codestral-latest"},
    ]
}

RAG_TOOLS = {
    "find_relevant_code": [
        {"provider": "mistral", "model": "codestral-latest"},
        {"provider": "groq", "model": "llama-3.3-70b-versatile"},
    ]
}

AUTO_MODELS = [
    {"provider": "mistral", "model": "mistral-large-latest"},
    {"provider": "mistral", "model": "codestral-latest"},
]

AUTO_CHAT_MODELS = [
    {"provider": "mistral", "model": "mistral-small-latest"},
    {"provider": "mistral", "model": "ministral-3b-2410"},
]

WATCHDOG_MODELS = [
    {"provider": "groq", "model": "llama-3.3-70b-versatile"},
    {"provider": "mistral", "model": "codestral-latest"},
]

MISTRAL_MODEL_NAMES = [
    "mistral-small-latest", "open-mistral-7b", "mistral-large-latest",
    "codestral-latest", "open-mistral-nemo", "ministral-3b-2410",
]