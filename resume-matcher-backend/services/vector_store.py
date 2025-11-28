# services/vector_store.py
"""
Vector Store Service for SmartSuccess.AI
Uses ChromaDB for persistent local vector storage
"""

import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings


class VectorStore:
    """ChromaDB wrapper for vector storage and retrieval"""
    
    def __init__(self):
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        print(f"ChromaDB initialized at: {persist_dir}")
    
    def _get_collection_name(self, user_id: str) -> str:
        clean_id = user_id.replace("-", "_").replace("@", "_at_")[:50]
        return f"user_{clean_id}"
    
    def get_or_create_collection(self, user_id: str):
        collection_name = self._get_collection_name(user_id)
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def upsert_documents(
        self, user_id: str, documents: List[str],
        embeddings: List[List[float]], metadatas: List[Dict], ids: List[str]
    ) -> Dict:
        collection = self.get_or_create_collection(user_id)
        try:
            collection.upsert(
                documents=documents, embeddings=embeddings,
                metadatas=metadatas, ids=ids
            )
            return {"status": "success", "documents_added": len(documents)}
        except Exception as e:
            print(f"Upsert error: {e}")
            raise
    
    async def query(
        self, user_id: str, query_embedding: List[float],
        n_results: int = 5, where_filter: Optional[Dict] = None
    ) -> Dict:
        collection = self.get_or_create_collection(user_id)
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_filter:
            query_params["where"] = where_filter
        try:
            return collection.query(**query_params)
        except Exception as e:
            print(f"Query error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    
    def delete_user_collection(self, user_id: str) -> bool:
        collection_name = self._get_collection_name(user_id)
        try:
            self.client.delete_collection(collection_name)
            return True
        except ValueError:
            return False

