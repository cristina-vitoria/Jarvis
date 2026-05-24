"""Ferramentas de RAG: recuperação de conteúdo e listagem de documentos.

Funções exportadas:
    buscar_material_rag(pergunta, vectorstore, llm_fn) -> str
"""

from src.rag.retriever import recuperar

SCORE_MINIMO = 0.30   # abaixo disso o chunk é considerado irrelevante


def buscar_material_rag(pergunta: str, vectorstore, llm_fn) -> str:
    """
    Recupera trechos relevantes dos materiais de estudo e gera uma resposta.

    Args:
        pergunta: pergunta acadêmica do usuário.
        vectorstore: índice FAISS com os documentos.
        llm_fn: função que recebe lista de mensagens e retorna string.

    Returns:
        Resposta gerada com base nos documentos recuperados.
    """
    chunks = recuperar(pergunta, vectorstore)
    chunks = [c for c in chunks if c.get("score", 0) >= SCORE_MINIMO]

    if not chunks:
        return "Não encontrei trechos suficientemente relevantes nos materiais."

    contexto = "\n\n---\n\n".join(
        f"[Fonte: {_label_chunk(c)}]\n{c['texto']}" for c in chunks
    )

    # Fontes únicas — usa title quando disponível, senão nome do arquivo
    fontes_unicas = list({
        _label_chunk(c): None for c in chunks
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
    """Retorna o rótulo de exibição de um chunk: title se disponível, senão fonte."""
    return chunk.get("title") or chunk.get("fonte", "desconhecido")