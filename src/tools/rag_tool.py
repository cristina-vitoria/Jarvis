"""Ferramenta de RAG: recupera chunks e gera resposta fundamentada.

Importa o revisor de `llm_client` para aplicar self-correction antes
de retornar a resposta final ao usuário.
"""

from src.rag.retriever import recuperar

MAX_RETRIES = 2  # Número máximo de tentativas de regeração

SCORE_MINIMO = 0.30   # abaixo disso, o chunk é irrelevante


def buscar_material_rag(pergunta: str, vectorstore, llm_fn) -> str:
    """
    Recupera trechos relevantes dos materiais de estudo e gera uma resposta

    Args:
        pergunta: pergunta acadêmica do usuário.
        vectorstore: índice FAISS com os documentos.
        llm_fn: função que recebe lista de mensagens e retorna string.

    Returns:
        Resposta gerada e validada com base nos documentos recuperados.
    """
    chunks = recuperar(pergunta, vectorstore)

    # Filtra chunks com score baixo — mais confiável que um revisor LLM
    chunks = [c for c in chunks if c.get("score", 0) >= SCORE_MINIMO]

    if not chunks:
        return "Não encontrei trechos suficientemente relevantes nos materiais."

    contexto = "\n\n---\n\n".join(
        f"[Fonte: {c['fonte']}]\n{c['texto']}" for c in chunks
    )
    fontes = list({c["fonte"] for c in chunks})

    messages = [
        {"role": "system", "content": (
            "Você é um assistente acadêmico. Responda usando APENAS o contexto. Não invente."
            "Se a resposta não estiver no contexto, diga isso claramente. "
            "Cite as fontes ao final."
        )},
        {"role": "user", "content": f"Contexto:\n{contexto}\n\nPergunta: {pergunta}"},
    ]

    resposta = llm_fn(messages)
    return f"{resposta}\n\n📚 Fontes consultadas: {', '.join(fontes)}"