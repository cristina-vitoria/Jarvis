"""Ferramentas de RAG: recuperação de conteúdo e listagem de documentos.

Funções exportadas:
    buscar_material_rag(pergunta, vectorstore, llm_fn) -> str
"""

from src.rag.retriever import recuperar

SCORE_MINIMO = 0.30   # abaixo disso o chunk é considerado irrelevante


def _score_efetivo(chunk: dict) -> float:
    """Retorna o score mais relevante disponível no chunk.

    Prioridade:
        1. reranker_score — presente quando RAG_RERANKER=true (Cross-Encoder, 0-1 via sigmoid)
        2. rrf_score      — presente quando RAG_HYBRID_ENABLED=true (Reciprocal Rank Fusion)
        3. score          — busca semântica pura (similaridade de cosseno FAISS)

    O SCORE_MINIMO é calibrado para valores de cosseno (0-1). Para rrf_score
    e reranker_score os valores também ficam nessa faixa, então o limiar é
    aplicável nos três casos.
    """
    for campo in ("reranker_score", "rrf_score", "score"):
        valor = chunk.get(campo)
        if valor is not None:
            return float(valor)
    return 0.0


def buscar_material_rag(pergunta: str, vectorstore, llm_fn, bm25_store=None) -> str:
    """
    Recupera trechos relevantes dos materiais de estudo e gera uma resposta.

    Args:
        pergunta: pergunta acadêmica do usuário.
        vectorstore: índice FAISS com os documentos.
        llm_fn: função que recebe lista de mensagens e retorna string.

    Returns:
        Resposta gerada com base nos documentos recuperados.
    """
    chunks = recuperar(pergunta, vectorstore, llm_fn=llm_fn, bm25_store=bm25_store)
    chunks = [c for c in chunks if _score_efetivo(c) >= SCORE_MINIMO]

    if not chunks:
        return "Não encontrei trechos suficientemente relevantes nos materiais."

    # Monta o contexto incluindo o heading_secao quando disponível,
    # para que a LLM saiba de qual seção do slide cada trecho veio.
    partes_contexto = []
    for c in chunks:
        label = _label_chunk(c)
        heading = c.get("heading_secao", "").strip()
        if heading:
            partes_contexto.append(f"[Fonte: {label} — Seção: {heading}]\n{c['texto']}")
        else:
            partes_contexto.append(f"[Fonte: {label}]\n{c['texto']}")

    contexto = "\n\n---\n\n".join(partes_contexto)

    # Fontes únicas — inclui heading quando disponível
    fontes_unicas = list({
        _label_fonte_completo(c): None for c in chunks
    }.keys())

    messages = [
        {
            "role": "system",
            "content": (
                "Você é um assistente acadêmico. Responda usando APENAS o contexto fornecido. "
                "Não invente informações. Se a resposta não estiver no contexto, diga isso claramente. "
                "Cite as fontes ao final."
            ),
        },
        {
            "role": "user",
            "content": f"Contexto:\n{contexto}\n\nPergunta: {pergunta}",
        },
    ]

    resposta = llm_fn(messages)
    return f"{resposta}\n\n📚 Fontes consultadas: {', '.join(fontes_unicas)}"


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _label_chunk(chunk: dict) -> str:
    """Retorna o rótulo de documento de um chunk: title se disponível, senão fonte."""
    return chunk.get("title") or chunk.get("fonte", "desconhecido")


def _label_fonte_completo(chunk: dict) -> str:
    """
    Rótulo completo para exibição ao usuário:
    '<título_doc> — <heading_secao>' ou apenas '<título_doc>'.
    Garante que fontes com headings diferentes aparecem separadas na lista.
    """
    doc_label = _label_chunk(chunk)
    heading = chunk.get("heading_secao", "").strip()
    if heading:
        return f"{doc_label} — {heading}"
    return doc_label
