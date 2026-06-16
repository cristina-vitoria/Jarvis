"""Busca Híbrida: funde resultados FAISS (semântico) + BM25 (léxico) via RRF.

Reciprocal Rank Fusion (RRF):
    score_rrf(doc) = sum_over_ranks( 1 / (k_rrf + rank_i) )

Onde k_rrf=60 é o valor padrão recomendado pela literatura (Cormack et al., 2009).
Esse método é robusto e não requer calibração de pesos entre os dois sistemas.

Fluxo:
    1. FAISS devolve top-N_dense por similaridade de cosseno.
    2. BM25 devolve top-N_sparse por pontuação BM25Okapi.
    3. RRF combina os dois rankings.
    4. Retorna os k_final melhores chunks.
"""

from __future__ import annotations

from src.config import RAG_TOP_K, RAG_HYBRID_N_DENSE, RAG_HYBRID_N_SPARSE

RRF_K = 60  # constante de suavização do RRF (60 é o padrão bibliográfico)


def _rrf_score(rank: int, k: int = RRF_K) -> float:
    return 1.0 / (k + rank + 1)  # +1 porque rank é 0-based


def recuperar_hibrido(
    pergunta: str,
    vectorstore,
    bm25_store,
    k: int = RAG_TOP_K,
    n_dense: int = RAG_HYBRID_N_DENSE,
    n_sparse: int = RAG_HYBRID_N_SPARSE,
) -> list[dict]:
    """Recupera chunks via busca híbrida FAISS + BM25 fundidos por RRF.

    Args:
        pergunta: query do usuário.
        vectorstore: instância de VectorStore (busca densa).
        bm25_store: instância de BM25Store (busca léxica).
        k: número final de chunks a retornar.
        n_dense: quantos candidatos buscar no FAISS antes da fusão.
        n_sparse: quantos candidatos buscar no BM25 antes da fusão.

    Returns:
        Lista de dicts com o campo adicional 'rrf_score'.
    """
    # 1. Busca densa (FAISS)
    resultados_densos = vectorstore.buscar(pergunta, k=n_dense)

    # 2. Busca léxica (BM25)
    resultados_bm25 = bm25_store.buscar(pergunta, k=n_sparse)

    # 3. Mapeia chunk_id → score RRF acumulado
    rrf_scores: dict[str, float] = {}
    chunk_por_id: dict[str, dict] = {}

    for rank, chunk in enumerate(resultados_densos):
        cid = str(chunk["id"])
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + _rrf_score(rank)
        chunk_por_id[cid] = chunk

    for rank, chunk in enumerate(resultados_bm25):
        cid = str(chunk["id"])
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + _rrf_score(rank)
        if cid not in chunk_por_id:
            chunk_por_id[cid] = chunk

    # 4. Ordena por score RRF decrescente e retorna os k melhores
    ordenados = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:k]

    resultado_final = []
    for cid, score in ordenados:
        chunk = dict(chunk_por_id[cid])
        chunk["rrf_score"] = score
        resultado_final.append(chunk)

    return resultado_final
