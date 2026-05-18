"""Construção e persistência do índice FAISS."""

import faiss
from src.rag.embeddings import gerar_embeddings


class VectorStore:
    """Armazena chunks e o índice FAISS para busca semântica."""

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        textos = [c["texto"] for c in chunks]
        embeddings = gerar_embeddings(textos)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner Product = cosseno com vetores normalizados
        self.index.add(embeddings)
        print(f"[VectorStore] Índice FAISS criado com {self.index.ntotal} vetores (dim={dim}).")

    def buscar(self, query: str, k: int = 3) -> list[dict]:
        """Retorna os k chunks mais relevantes para a query."""
        from src.rag.embeddings import gerar_embedding_query
        q_emb = gerar_embedding_query(query)
        distancias, indices = self.index.search(q_emb, k)
        resultados = []
        for score, idx in zip(distancias[0], indices[0]):
            if idx >= 0:
                chunk = dict(self.chunks[idx])
                chunk["score"] = float(score)
                resultados.append(chunk)
        return resultados


def construir_vectorstore(chunks: list[dict]) -> VectorStore:
    """Factory para criar e retornar um VectorStore."""
    return VectorStore(chunks)