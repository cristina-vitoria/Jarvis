"""BM25Store: índice BM25 para busca léxica sobre os chunks indexados.

Usa a biblioteca `rank_bm25` (BM25Okapi) para pontuar chunks por correspondência
exata de termos, complementando a busca semântica do FAISS.

A fusão dos dois rankings é feita por Reciprocal Rank Fusion (RRF) no
módulo `hybrid_retriever.py`.

Dependency: pip install rank-bm25
"""

from __future__ import annotations

import re
from typing import List

from rank_bm25 import BM25Okapi


def _tokenizar(texto: str) -> List[str]:
    """Tokeniza em lowercase, remove pontuação e split por espaços."""
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", " ", texto)
    return texto.split()


class BM25Store:
    """Encapsula o índice BM25 e exposes buscar()."""

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        corpus = [_tokenizar(c["texto"]) for c in chunks]
        self.bm25 = BM25Okapi(corpus)

    def buscar(self, query: str, k: int) -> list[dict]:
        """Retorna os k chunks com maior pontuação BM25.

        Args:
            query: string de busca.
            k: número de resultados a retornar.

        Returns:
            Lista de dicts com os campos do chunk mais 'bm25_score'.
        """
        tokens = _tokenizar(query)
        scores = self.bm25.get_scores(tokens)

        # Ordena por score decrescente e pega os k melhores
        top_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:k]

        resultados = []
        for idx in top_indices:
            chunk = dict(self.chunks[idx])
            chunk["bm25_score"] = float(scores[idx])
            resultados.append(chunk)
        return resultados
