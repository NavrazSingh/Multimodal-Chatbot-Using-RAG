import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import logging

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        logger.info(f"Initializing SentenceTransformer with model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        logger.info("VectorDBService initialized.")

    def add_documents(self, docs: list[str]):
        if not docs:
            return
        logger.info(f"Adding {len(docs)} documents to the index.")
        embeddings = self.model.encode(docs)
        self.index.add(np.array(embeddings).astype('float32'))
        self.documents.extend(docs)

    def search(self, query: str, top_k: int = 3) -> list[str]:
        if not self.documents:
            return []
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.documents):
                results.append(self.documents[idx])
        return results
