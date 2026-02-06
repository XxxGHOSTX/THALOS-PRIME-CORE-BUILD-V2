"""
Semantic Retrieval with Vector Store
Embedding-based similarity search for context retrieval
"""

import numpy as np
import hashlib as hl
from datetime import datetime as dt


class VectorStore:
    """In-memory vector store for embeddings"""
    
    def __init__(self, dim=512):
        self.dim = dim
        self.vectors = []
        self.metadata = []
        self.ids = []
        
    def add(self, vec, meta, vec_id=None):
        """Add vector to store"""
        if len(vec) != self.dim:
            raise ValueError(f"Vector dimension {len(vec)} != store dimension {self.dim}")
            
        if vec_id is None:
            vec_id = hl.sha256(f"{dt.now().isoformat()}{len(self.vectors)}".encode()).hexdigest()[:16]
            
        self.vectors.append(np.array(vec))
        self.metadata.append(meta)
        self.ids.append(vec_id)
        
        return vec_id
    
    def search(self, query_vec, top_k=5):
        """Find most similar vectors"""
        if not self.vectors:
            return []
            
        query_vec = np.array(query_vec)
        if len(query_vec) != self.dim:
            raise ValueError(f"Query dimension {len(query_vec)} != store dimension {self.dim}")
            
        # Compute cosine similarity
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []
            
        similarities = []
        for i, vec in enumerate(self.vectors):
            vec_norm = np.linalg.norm(vec)
            if vec_norm == 0:
                sim = 0.0
            else:
                sim = float(np.dot(query_vec, vec) / (query_norm * vec_norm))
            similarities.append((sim, i))
            
        # Sort by similarity
        similarities.sort(reverse=True)
        
        # Return top k
        results = []
        for sim, idx in similarities[:top_k]:
            results.append({
                'id': self.ids[idx],
                'similarity': sim,
                'metadata': self.metadata[idx],
                'vector': self.vectors[idx]
            })
            
        return results
    
    def get_stats(self):
        """Get store statistics"""
        return {
            'dimension': self.dim,
            'vectors': len(self.vectors),
            'total_memory': len(self.vectors) * self.dim * 8  # bytes
        }


class SemanticRetriever:
    """Semantic retrieval engine with embedding generation"""
    
    def __init__(self, dim=512):
        self.dim = dim
        self.vector_store = VectorStore(dim)
        self.query_history = []
        
    def embed_text(self, txt):
        """Generate embedding for text"""
        # Simple but effective text embedding using character-level features
        vec = np.zeros(self.dim)
        
        # Character frequency features
        for i, ch in enumerate(txt[:self.dim]):
            ch_val = ord(ch) / 1114112.0
            pos_enc = np.sin(i / len(txt) * np.pi) if len(txt) > 0 else 0.0
            vec[i % self.dim] += ch_val * (1.0 + pos_enc * 0.3)
            
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
            
        # Add semantic features (word patterns)
        words = txt.lower().split()
        for i, word in enumerate(words[:32]):
            word_hash = int(hl.md5(word.encode()).hexdigest()[:8], 16)
            idx = word_hash % self.dim
            vec[idx] += 0.1 * (1.0 - i / len(words))
            
        # Re-normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
            
        return vec
    
    def index_document(self, text, metadata=None):
        """Index document for retrieval"""
        embedding = self.embed_text(text)
        
        meta = metadata or {}
        meta['text'] = text[:200]  # Store preview
        meta['length'] = len(text)
        meta['timestamp'] = dt.now().isoformat()
        
        doc_id = self.vector_store.add(embedding, meta)
        return doc_id
    
    def retrieve(self, query, top_k=5):
        """Retrieve most relevant documents"""
        query_vec = self.embed_text(query)
        results = self.vector_store.search(query_vec, top_k)
        
        # Log query
        self.query_history.append({
            'query': query,
            'timestamp': dt.now().isoformat(),
            'results': len(results)
        })
        
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-1000:]
            
        return results
    
    def batch_index(self, documents):
        """Index multiple documents"""
        doc_ids = []
        for doc in documents:
            if isinstance(doc, str):
                doc_id = self.index_document(doc)
            else:
                doc_id = self.index_document(doc.get('text', ''), doc.get('metadata'))
            doc_ids.append(doc_id)
        return doc_ids
    
    def get_metrics(self):
        """Get retrieval metrics"""
        store_stats = self.vector_store.get_stats()
        
        return {
            'indexed_documents': store_stats['vectors'],
            'query_history': len(self.query_history),
            'vector_dimension': self.dim,
            'memory_usage_bytes': store_stats['total_memory']
        }
