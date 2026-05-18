"""Ferramenta de RAG: recupera chunks e gera resposta fundamentada."""

from src.rag.retriever import recuperar


def buscar_material_rag(pergunta: str, vectorstore, llm_fn) -> str:
    """
    Recupera trechos relevantes dos materiais de estudo e gera uma resposta.

    Args:
        pergunta: pergunta acadêmica do usuário.
        vectorstore: índice FAISS com os documentos.
        llm_fn: função que recebe uma lista de mensagens e retorna string.

    Returns:
        Resposta gerada com base nos documentos recuperados.
    """
    chunks = recuperar(pergunta, vectorstore)

    if not chunks:
        return "Não encontrei trechos relevantes nos materiais sobre esse assunto."

    contexto = "\n\n---\n\n".join(
        f"[Fonte: {c['fonte']}]\n{c['texto']}" for c in chunks
    )
    fontes = list({c['fonte'] for c in chunks})

    messages = [
        {
            "role": "system",
            "content": (
                "Você é um assistente acadêmico. Responda à pergunta do aluno "
                "usando APENAS as informações do contexto abaixo. "
                "Se a resposta não estiver no contexto, diga que não encontrou nos materiais. "
                "Cite as fontes ao final."
            ),
        },
        {
            "role": "user",
            "content": f"Contexto:\n{contexto}\n\nPergunta: {pergunta}",
        },
    ]

    resposta = llm_fn(messages)
    return f"{resposta}\n\n📚 Fontes consultadas: {', '.join(fontes)}"