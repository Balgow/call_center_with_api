import faiss
import pickle
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Optional
# import torch
# from sentence_transformers import SentenceTransformer
from dataclasses import dataclass
from ..utils.logger import default_logger, timing_decorator
from ..utils.config import BASE_DIR, EMBEDDING_MODEL_SETTINGS, ISSAI_MODEL_SETTINGS


@dataclass
class QADocument:
    """Data class for QA documents"""
    id: str
    question: str
    answer: str
    lang: str
    source: str
    type: str = "qa"

class DocumentLoader:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or BASE_DIR / "data"
        self.index, self.metadata = self.load_document()
        self.load_embedding_model()
        print("Loaded FAISS index")

    def load_embedding_model(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_SETTINGS['path'], device='cuda')


    def load_document(self):
        index = faiss.read_index(f"{self.data_dir}/full_ru_docs/index.faiss")
        with open(f"{self.data_dir}/full_ru_docs/metadata.pkl", "rb") as f:
            metadata = pickle.load(f)
        return index, metadata
    
    def get_query_embedding(self, query):
        return self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
    @timing_decorator(default_logger)
    def search_document(self, query):
        query_vector = self.get_query_embedding(query)
        distances, indices = self.index.search(query_vector, EMBEDDING_MODEL_SETTINGS["top_k"])
        print(distances)
        results = []
        for i, idx in enumerate(indices[0]):
            if distances[0][i] >= EMBEDDING_MODEL_SETTINGS["threshold"]:
                results.append(self.metadata[idx])
        return results
    
    def construct_prompt_message(self, user_question, context_chunks) -> List[Dict[str, str]]:
        context_text = "\n\n".join(context_chunks)
        messages = [
            {"role": "system", "content": ISSAI_MODEL_SETTINGS["system_prompt"]},
            {"role": "user", "content": f"{user_question}\n\nКонтекст:\n{context_text}"}
        ]
        return messages