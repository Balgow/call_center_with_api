import re
from typing import Optional, List, Dict
from ..utils.logger import default_logger, timing_decorator
from transformers import pipeline
from ..utils.config import ISSAI_MODEL_SETTINGS, FASTAPI_SETTINGS
import httpx
class GPTHandler:
    def __init__(self):
        self.url = FASTAPI_SETTINGS['host']
        
    #     self.logger = default_logger.getChild("GPTHandler")
    #     self.model = None
        
    #     self._initialize_local_model()

    # def _initialize_local_model(self):
    #     """Initialize the local transformer model pipeline"""
    #     try:
    #         self.model = pipeline("text-generation", model=ISSAI_MODEL_SETTINGS['path'])
    #     except Exception as e:
    #         self.logger.warning(f"Failed to initialize local model: {e}")

    # @timing_decorator(default_logger)
    # def generate_response_from_messages(self, messages: List[Dict[str, str]]) -> Optional[str]:
        # """Generate response using local transformer model"""
        # try:
        #     if not self.model:
        #         self.logger.error("Local model pipeline not initialized")
        #         return None
            
        #     result = self.model(messages)
            
        #     if result and len(result) > 0:
        #         return result[0].get('generated_text', '')[2]['content']
        #     return None
            
        # except Exception as e:
        #     self.logger.error(f"Error generating local model response: {e}")
        #     return None

    @timing_decorator(default_logger)
    def generate_response_from_text(self, text: str) -> Optional[str]:
        response = httpx.post(self.url, json={"text": text}, timeout=60)
        print(response.json())
        return response.json()["response"]


    # @timing_decorator(default_logger)
    # def generate_response_from_text(self, text: str) -> Optional[str]:
    #     """Generate response from plain text using local model"""
    #     messages = [
    #         {"role": "system", "content": ISSAI_MODEL_SETTINGS['system_prompt']},
    #         {"role": "user", "content": text}
    #         ]
    #     return self.generate_response_from_messages(messages)
        
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
