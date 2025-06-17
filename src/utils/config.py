from environs import Env
from pathlib import Path
import time

env = Env()
env.read_env()

BASE_DIR = Path(__file__).parent.parent.parent
AUDIO_DIR = BASE_DIR / "audio_files"
AUDIO_DIR.mkdir(exist_ok=True)

# Yandex settings
YANDEX_API_KEY = env.str("YANDEX_API_KEY", 'TEST_YANDEX_API_KEY')


# Audio settings
AUDIO_SETTINGS = {
    "FORMAT": "paInt16",
    "CHANNELS": 1,
    "RATE": 8000,
    "CHUNK": 4096,
    "RECORD_SECONDS": 30,
    "WAVE_OUTPUT_FILENAME": str(AUDIO_DIR / f"{time.time()}.wav")
}

# GPT settings
GPT_SETTINGS_v1 = {
    "model": "gpt-4o-mini",
    "embedding_model": "text-embedding-3-small",
    "threshold": 1.4,
    "top_k": 1,
    "temperature": 0.2,
    "max_tokens": 100,
    "top_p": 1.0,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0,
    "system_prompt": "You are a helpful assistant for a railway ticketing platform. Answer user questions briefly and accurately using the context.",
}

GPT_SETTINGS_v2 = {
    "model": "gpt-4o-mini",
    "embedding_model": "text-embedding-3-small",
    "threshold": 1.7,
    "top_k": 2,
    "temperature": 0.2,
    "max_tokens": 100,
    "top_p": 1.0,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0,
    "system_prompt": "You are a helpful assistant for a railway ticketing service. Answer user questions briefly and clearly using only the provided context. Do not use bullet points or lists."
}

GPT_SETTINGS_v3 = {
    "model": "gpt-4o-mini",
    "embedding_model": "text-embedding-3-small",
    "threshold": 1.7,
    "top_k": 1,
    "temperature": 0.2,
    "max_tokens": 100,
    "top_p": 1.0,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0,
    "system_prompt": "You are a helpful assistant for a railway ticketing platform. Answer user questions briefly and accurately using the context."
}

ISSAI_MODEL_SETTINGS = {
    'path': f'{BASE_DIR}/issai_model',
    "system_prompt": "You are a helpful assistant for a railway ticketing platform. Answer user questions briefly and accurately using the context."
}


EMBEDDING_MODEL_SETTINGS = {
    'path' : f'{BASE_DIR}/embedding_model',
    'top_k': 1,    
    'threshold': 0.45,
}

FASTAPI_SETTINGS = {
    "host": "https://f021-37-208-42-227.ngrok-free.app/process_text",
}

DOCUMENT_START = "Здравствуйте! Чем я могу помочь?"
DOCUMENT_NON_EXISTING = "Пожалуйста, сформулируйте вопрос по-другому."
DOCUMENT_END = "Могу я чем-то еще помочь?"