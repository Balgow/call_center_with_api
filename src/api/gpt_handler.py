import re
from typing import Optional, List, Dict
from ..utils.logger import default_logger, timing_decorator
from transformers import pipeline
from ..utils.config import ISSAI_MODEL_SETTINGS, FASTAPI_SETTINGS
import httpx
class GPTHandler:
    def __init__(self):
        self.url = FASTAPI_SETTINGS['host']
        
    @timing_decorator(default_logger)
    def generate_response_from_text(self, text: str) -> Optional[str]:
        response = httpx.post(self.url, json={"text": text}, timeout=60)
        print(response.json())
        return response.json()["response"]
        
    def split_text_into_chunks(self, text, max_chars=250):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= max_chars:
                current += sentence + " "
            else:
                chunks.append(current.strip())
                current = sentence + " "
        if current:
            chunks.append(current.strip())

        return chunks
