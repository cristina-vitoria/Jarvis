"""Interface de recuperação de chunks para uso nas ferramentas.

Com Query Expansion habilitada (RAG_QUERY_EXPANSION=true no .env),
a pergunta é expandida via LLM antes de consultar o FAISS, aumentando
a probabilidade de recuperar chunks relevantes para perguntas genéricas
ou que usam vocabulário diferente do material indexado.
"""

from __future__ import annotations

from src.config import RAG_TOP_K, RAG_QUERY_EXPANSION


def recuperar(
    pergunta: str,
    vectorstore,
    k: int = RAG_TOP_K,
    llm_fn=None,
) -> list[dict]:
    """Recupera os chunks mais relevantes para a pergunta.

    Se RAG_QUERY_EXPANSION=true e llm_fn for fornecida, expande a query
    antes de consultar o FAISS. A busca é feita com a query expandida,
    mas os chunks retornados preservam o campo 'query_original'.

    Args:
        pergunta: query do usuário.
        vectorstore: instância de VectorStore.
        k: número de chunks a retornar.
        llm_fn: callable opcional para expansão (gerar_resposta do llm_client).

    Returns:
        Lista de dicts com os campos do chunk indexado mais 'score'.
        Campos garantidos: 'id', 'texto', 'fonte', 'estrategia_chunking', 'score'.
        Campo adicional: 'query_usada' (a query efetivamente buscada no FAISS).
    """
    query_busca = pergunta

    if RAG_QUERY_EXPANSION and llm_fn is not None:
        from src.rag.query_expansion import expandir_query
        query_busca = expandir_query(pergunta, llm_fn)

    resultados = vectorstore.buscar(query_busca, k=k)

    # Anota qual query foi efetivamente usada (útil para logs e debug)
    for chunk in resultados:
        chunk["query_usada"] = query_busca

    return resultados
