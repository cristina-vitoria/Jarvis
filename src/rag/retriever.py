"""Interface de recuperação de chunks para uso nas ferramentas.

Com Query Expansion habilitada (RAG_QUERY_EXPANSION=true no .env),
a pergunta é expandida via LLM antes de consultar o FAISS, aumentando
a probabilidade de recuperar chunks relevantes para perguntas genéricas
ou que usam vocabulário diferente do material indexado.

Quando RAG_RERANKER=true:
    1. Busca top-RAG_RERANKER_CANDIDATES no FAISS (mais candidatos).
    2. Passa os candidatos pelo Cross-Encoder (bge-reranker-base).
    3. Retorna apenas os RAG_TOP_K melhores após re-ranking.

Quando RAG_RERANKER=false:
    Comportamento padrão: retorna os chunks direto do FAISS.
"""

from __future__ import annotations

from src.config import (
    RAG_TOP_K,
    RAG_QUERY_EXPANSION,
    RAG_RERANKER,
    RAG_RERANKER_CANDIDATES,
)

from src.rag.query_expansion import expandir_query
from src.rag.reranker import rerankar



def recuperar(
    pergunta: str,
    vectorstore,
    k: int = RAG_TOP_K,
    llm_fn=None,
) -> list[dict]:
    """Recupera os chunks mais relevantes para a pergunta.

    Fluxo:
        1. Expande a query via LLM (opcional).
        2. Busca no FAISS.
        3. Re-ranqueia os candidatos (opcional).

    Args:
        pergunta: query do usuário.
        vectorstore: instância de VectorStore.
        k: número final de chunks a retornar.
        llm_fn: callable opcional para expansão (ex.: gerar_resposta do llm_client).

    Returns:
        Lista de dicts com os campos do chunk indexado.
        Campos garantidos: 'id', 'texto', 'fonte', 'estrategia_chunking'.
        Campos adicionais possíveis: 'score', 'reranker_score', 'query_usada'.
    """
    query_busca = pergunta

    # 1. Query Expansion
    if RAG_QUERY_EXPANSION and llm_fn is not None:
        query_busca = expandir_query(pergunta, llm_fn)

    # 2. Busca + Re-ranking opcional
    if RAG_RERANKER:
        candidatos = vectorstore.buscar(query_busca, k=RAG_RERANKER_CANDIDATES)
        resultados = rerankar(pergunta, candidatos, top_k=k)
    else:
        resultados = vectorstore.buscar(query_busca, k=k)

    # 3. Guarda a query usada na recuperação
    for chunk in resultados:
        chunk["query_usada"] = query_busca

    return resultados