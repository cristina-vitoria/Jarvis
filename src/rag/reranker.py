"""Re-ranking com Cross-Encoder para refinar os candidatos do FAISS.

Fluxo:
    1. retriever.py busca os top-N candidatos no FAISS (N >> RAG_TOP_K).
    2. O Cross-Encoder pontua cada par (pergunta, chunk) individualmente,
       capturando interações semânticas que o bi-encoder não consegue.
    3. Os k melhores chunks são retornados para a LLM principal.

Modelo padrão: BAAI/bge-reranker-base
    - ~280MB, roda em CPU em ~100ms para 15 chunks
    - Score de 0 a 1 via sigmoid (lógits brutos transformados)

Dependency: pip install sentence-transformers  (já no requirements.txt)
"""

from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

RERANKER_MODEL = "BAAI/bge-reranker-base"


@lru_cache(maxsize=1)
def _get_reranker():
    """Carrega o Cross-Encoder uma única vez (lazy + cached)."""
    from sentence_transformers import CrossEncoder  # noqa: PLC0415
    logger.info("[Reranker] Carregando modelo '%s'...", RERANKER_MODEL)
    model = CrossEncoder(RERANKER_MODEL, max_length=512)
    logger.info("[Reranker] Modelo carregado.")
    return model


def rerankar(
    pergunta: str,
    chunks: list[dict],
    top_k: int,
) -> list[dict]:
    """Reordena `chunks` pelo score do Cross-Encoder e retorna os `top_k` melhores.

    Args:
        pergunta: query original do usuário.
        chunks: lista de candidatos já recuperados pelo FAISS.
        top_k: quantos chunks retornar após o re-ranking.

    Returns:
        Lista de até `top_k` chunks com campo adicional 'reranker_score' (float).
    """
    if not chunks:
        return []

    model = _get_reranker()

    # Cria pares (pergunta, texto_do_chunk) para o Cross-Encoder
    pares = [(pergunta, c["texto"]) for c in chunks]
    scores = model.predict(pares)  # array de logits ou scores

    # Converte para float e anota no chunk
    chunks_pontuados = []
    for chunk, score in zip(chunks, scores):
        c = dict(chunk)
        c["reranker_score"] = float(score)
        chunks_pontuados.append(c)

    # Ordena por score decrescente e corta em top_k
    chunks_pontuados.sort(key=lambda x: x["reranker_score"], reverse=True)

    resultado = chunks_pontuados[:top_k]
    logger.debug(
        "[Reranker] %d candidatos → %d selecionados. Top score: %.4f",
        len(chunks),
        len(resultado),
        resultado[0]["reranker_score"] if resultado else 0.0,
    )
    return resultado
