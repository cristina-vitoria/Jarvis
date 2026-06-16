"""Interface de recuperação de chunks para uso nas ferramentas.

Quando RAG_RERANKER=true:
    1. Busca top-RAG_RERANKER_CANDIDATES no FAISS (mais candidatos).
    2. Passa os candidatos pelo Cross-Encoder (bge-reranker-base).
    3. Retorna apenas os RAG_TOP_K melhores após re-ranking.

Quando RAG_RERANKER=false (padrão):
    Comportamento original: retorna os RAG_TOP_K direto do FAISS.
"""

from __future__ import annotations

from src.config import RAG_TOP_K, RAG_RERANKER, RAG_RERANKER_CANDIDATES


def recuperar(
    pergunta: str,
    vectorstore,
    k: int = RAG_TOP_K,
) -> list[dict]:
    """Recupera os chunks mais relevantes para a pergunta.

    Args:
        pergunta: query do usuário.
        vectorstore: instância de VectorStore.
        k: número de chunks a retornar (após re-ranking, se ativo).

    Returns:
        Lista de dicts com os campos do chunk indexado mais 'score'.
        Com re-ranking: inclui também 'reranker_score'.
    """
    if RAG_RERANKER:
        # Busca mais candidatos para o Cross-Encoder filtrar
        candidatos = vectorstore.buscar(pergunta, k=RAG_RERANKER_CANDIDATES)
        from src.rag.reranker import rerankar  # noqa: PLC0415
        return rerankar(pergunta, candidatos, top_k=k)

    return vectorstore.buscar(pergunta, k=k)
