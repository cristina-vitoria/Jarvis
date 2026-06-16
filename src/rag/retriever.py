"""Interface de recuperação de chunks para uso nas ferramentas.

Fluxo completo (todos os módulos ativos):

    Pergunta do usuário
        │
        ▼
    [1] Query Strategy (RAG_QUERY_EXPANSION=true)
        │  mode='expansion' → adiciona sinônimos/termos técnicos à query
        │  mode='hyde'      → gera documento hipotético (HyDE) como query
        │  fallback         → usa a pergunta original
        ▼
    [2] Busca
        │  RAG_HYBRID_ENABLED=true  → FAISS (denso) + BM25 (léxico) fusionados por RRF
        │  RAG_HYBRID_ENABLED=false → FAISS puro
        ▼
    [3] Re-ranking (RAG_RERANKER=true)
        │  Cross-Encoder reordena os candidatos pela pergunta ORIGINAL
        │  (não pela query expandida/HyDE, para preservar fidelidade semântica)
        ▼
    RAG_TOP_K chunks finais

Nota sobre HyDE + Re-ranking:
    No passo [3], o re-ranking usa sempre a pergunta original do usuário,
    não o documento hipotético. Isso é intencional: o HyDE serve apenas
    para aproximar o vetor de busca dos vetores dos chunks no espaço de
    embeddings. A avaliação de relevância final deve ser feita contra
    a intenção real do usuário.
"""

from __future__ import annotations

from src.config import (
    RAG_TOP_K,
    RAG_QUERY_EXPANSION,
    RAG_RERANKER,
    RAG_RERANKER_CANDIDATES,
    RAG_HYBRID_ENABLED,
)
from src.rag.query_expansion import aplicar_query_strategy
from src.rag.reranker import rerankar
from src.rag.hybrid_retriever import recuperar_hibrido


def recuperar(
    pergunta: str,
    vectorstore,
    k: int = RAG_TOP_K,
    llm_fn=None,
    bm25_store=None,
) -> list[dict]:
    """Recupera os chunks mais relevantes para a pergunta.

    Args:
        pergunta: query original do usuário.
        vectorstore: instância de VectorStore (FAISS).
        k: número final de chunks a retornar.
        llm_fn: callable opcional para Query Expansion / HyDE.
                Se None, a etapa de transformação de query é pulada.
        bm25_store: instância de BM25Store opcional para busca híbrida.

    Returns:
        Lista de dicts com os campos do chunk indexado.
        Campos garantidos: 'id', 'texto', 'fonte', 'estrategia_chunking'.
        Campos adicionais possíveis: 'score', 'rrf_score', 'reranker_score',
        'query_usada', 'query_strategy'.
    """
    query_busca = pergunta
    query_strategy = "original"

    # ------------------------------------------------------------------
    # 1. Transformação de query (Expansion ou HyDE)
    # ------------------------------------------------------------------
    if RAG_QUERY_EXPANSION and llm_fn is not None:
        from src.config import RAG_QUERY_EXPANSION_MODE
        query_busca = aplicar_query_strategy(pergunta, llm_fn)
        query_strategy = RAG_QUERY_EXPANSION_MODE.lower().strip()

    # ------------------------------------------------------------------
    # 2. Busca: híbrida (FAISS + BM25 via RRF) ou semântica pura
    # ------------------------------------------------------------------
    n_candidatos = RAG_RERANKER_CANDIDATES if RAG_RERANKER else k

    if RAG_HYBRID_ENABLED:
        candidatos_base = recuperar_hibrido(
            query_busca, vectorstore, bm25_store, k=n_candidatos
        )
    elif RAG_RERANKER:
        candidatos_base = vectorstore.buscar(query_busca, k=RAG_RERANKER_CANDIDATES)
    else:
        candidatos_base = vectorstore.buscar(query_busca, k=k)

    # ------------------------------------------------------------------
    # 3. Re-ranking com Cross-Encoder
    #    Usa a pergunta ORIGINAL (não a expandida/HyDE) para avaliar
    #    a relevância final dos candidatos.
    # ------------------------------------------------------------------
    if RAG_RERANKER:
        resultados = rerankar(pergunta, candidatos_base, top_k=k)
    else:
        resultados = candidatos_base[:k]

    # ------------------------------------------------------------------
    # 4. Anota metadados de rastreabilidade em cada chunk
    # ------------------------------------------------------------------
    for chunk in resultados:
        chunk["query_usada"] = query_busca
        chunk["query_strategy"] = query_strategy

    return resultados
