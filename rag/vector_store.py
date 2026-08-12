"""
Local Vector Store and Cosine Similarity Retrieval Engine for Medical Protocols.
Operates 100% offline with zero external cloud dependencies.
"""
import os
import json
import re
import math
from typing import List, Dict, Any, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROTOCOLS_FILE = os.path.join(BASE_DIR, "knowledge", "ssv_protocols.json")


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into lowercase terms."""
    if not text:
        return []
    words = re.findall(r'\w+', text.lower())
    return [w for w in words if len(w) > 2]


class LocalVectorStore:
    """
    Offline Vector Store using TF-IDF & Cosine Similarity search over protocol documents.
    """

    def __init__(self, json_path: str = PROTOCOLS_FILE):
        self.json_path = json_path
        self.documents: List[Dict[str, Any]] = []
        self.vocab: Dict[str, int] = {}
        self.doc_vectors: List[Dict[str, float]] = []
        self.idf: Dict[str, float] = {}
        self.load_and_index()

    def load_and_index(self):
        """Load JSON knowledge base and build local inverted TF-IDF index."""
        if not os.path.exists(self.json_path):
            return

        with open(self.json_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        num_docs = len(self.documents)
        if num_docs == 0:
            return

        # Calculate Term Frequency (TF) per doc and Document Frequency (DF)
        df: Dict[str, int] = {}
        tf_docs: List[Dict[str, float]] = []

        for doc in self.documents:
            full_text = f"{doc.get('disease', '')} {doc.get('title_uz', '')} {doc.get('title_ru', '')} {doc.get('title_en', '')} {doc.get('content_uz', '')} {doc.get('content_ru', '')} {doc.get('content_en', '')} {' '.join(doc.get('tags', []))}"
            tokens = tokenize(full_text)
            term_counts: Dict[str, int] = {}
            for t in tokens:
                term_counts[t] = term_counts.get(t, 0) + 1

            doc_tf: Dict[str, float] = {}
            total_terms = len(tokens) or 1
            for term, count in term_counts.items():
                doc_tf[term] = count / total_terms
                df[term] = df.get(term, 0) + 1

            tf_docs.append(doc_tf)

        # Calculate Inverse Document Frequency (IDF)
        for term, doc_freq in df.items():
            self.idf[term] = math.log((1 + num_docs) / (1 + doc_freq)) + 1.0

        # Build TF-IDF vectors
        self.doc_vectors = []
        for doc_tf in tf_docs:
            vector: Dict[str, float] = {}
            for term, tf_val in doc_tf.items():
                vector[term] = tf_val * self.idf.get(term, 1.0)
            self.doc_vectors.append(vector)

    def _vector_norm(self, vec: Dict[str, float]) -> float:
        return math.sqrt(sum(v * v for v in vec.values())) or 1.0

    def search(self, query: str, top_k: int = 2, lang: str = "uz") -> List[Tuple[Dict[str, Any], float]]:
        """
        Perform Cosine Similarity Vector Search for a query.
        Returns top-K matching protocols with similarity scores.
        """
        query_tokens = tokenize(query)
        if not query_tokens or not self.documents:
            return []

        # Build query vector
        query_tf: Dict[str, float] = {}
        total = len(query_tokens)
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0) + 1

        query_vec: Dict[str, float] = {}
        for term, count in query_tf.items():
            tf_val = count / total
            query_vec[term] = tf_val * self.idf.get(term, 1.0)

        q_norm = self._vector_norm(query_vec)

        # Cosine distance ranking
        results: List[Tuple[Dict[str, Any], float]] = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            dot_product = sum(query_vec[t] * doc_vec[t] for t in query_vec if t in doc_vec)
            d_norm = self._vector_norm(doc_vec)
            sim_score = dot_product / (q_norm * d_norm)

            if sim_score > 0.01 or any(t in tokenize(self.documents[idx].get('disease', '')) for t in query_tokens):
                results.append((self.documents[idx], sim_score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


# Singleton Local Vector Store Instance
_vector_store_instance = None


def get_vector_store() -> LocalVectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = LocalVectorStore()
    return _vector_store_instance
