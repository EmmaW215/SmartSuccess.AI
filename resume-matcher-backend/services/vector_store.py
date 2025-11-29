# services/vector_store.py
"""
Vector Store Service for SmartSuccess.AI
Lightweight in-memory vector storage (no ChromaDB dependency)
Uses cosine similarity for vector search
"""

import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class VectorDocument:
    """Single document with its embedding"""
    id: str
    document: str
    embedding: List[float]
    metadata: Dict


class VectorStore:
    """Lightweight in-memory vector store using numpy for similarity search"""
    
    def __init__(self):
        # Store collections per user: {user_id: [VectorDocument, ...]}
        self.collections: Dict[str, List[VectorDocument]] = {}
        print("Lightweight VectorStore initialized (in-memory)")
    
    def _get_collection_name(self, user_id: str) -> str:
        """Generate clean collection key from user_id"""
        clean_id = user_id.replace("-", "_").replace("@", "_at_")[:50]
        return f"user_{clean_id}"
    
    def get_or_create_collection(self, user_id: str) -> List[VectorDocument]:
        """Get or create a collection for a user"""
        collection_name = self._get_collection_name(user_id)
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        return self.collections[collection_name]
    
    async def upsert_documents(
        self, user_id: str, documents: List[str],
        embeddings: List[List[float]], metadatas: List[Dict], ids: List[str]
    ) -> Dict:
        """Add or update documents in the collection"""
        collection_name = self._get_collection_name(user_id)
        
        # Create new collection (replacing old one)
        self.collections[collection_name] = []
        collection = self.collections[collection_name]
        
        for doc, emb, meta, doc_id in zip(documents, embeddings, metadatas, ids):
            collection.append(VectorDocument(
                id=doc_id,
                document=doc,
                embedding=emb,
                metadata=meta
            ))
        
        return {"status": "success", "documents_added": len(documents)}
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a = np.array(vec1)
        b = np.array(vec2)
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    async def query(
        self, user_id: str, query_embedding: List[float],
        n_results: int = 5, where_filter: Optional[Dict] = None
    ) -> Dict:
        """Query the collection for similar documents"""
        collection_name = self._get_collection_name(user_id)
        
        if collection_name not in self.collections:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        collection = self.collections[collection_name]
        
        if not collection:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        # Calculate similarities
        results = []
        for doc in collection:
            # Apply filter if specified
            if where_filter:
                match = all(
                    doc.metadata.get(k) == v 
                    for k, v in where_filter.items()
                )
                if not match:
                    continue
            
            similarity = self._cosine_similarity(query_embedding, doc.embedding)
            # Convert similarity to distance (1 - similarity for cosine)
            distance = 1 - similarity
            results.append((doc, distance))
        
        # Sort by distance (ascending - lower is better)
        results.sort(key=lambda x: x[1])
        
        # Take top n_results
        top_results = results[:n_results]
        
        documents = [r[0].document for r in top_results]
        metadatas = [r[0].metadata for r in top_results]
        distances = [r[1] for r in top_results]
        
        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances]
        }
    
    def delete_user_collection(self, user_id: str) -> bool:
        """Delete a user's collection"""
        collection_name = self._get_collection_name(user_id)
        if collection_name in self.collections:
            del self.collections[collection_name]
            return True
        return False
    
    def get_collection_stats(self, user_id: str) -> Dict:
        """Get statistics about a user's collection"""
        collection_name = self._get_collection_name(user_id)
        if collection_name not in self.collections:
            return {"exists": False, "document_count": 0}
        
        collection = self.collections[collection_name]
        return {
            "exists": True,
            "document_count": len(collection)
        }
