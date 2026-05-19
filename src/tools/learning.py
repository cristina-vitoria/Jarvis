"""Ferramentas de aprendizado: geração de exercícios e quiz interativo."""

from src.rag.retriever import recuperar


def gerar_exercicios(topico: str, vectorstore, llm_fn, quantidade: int = 3) -> str:
    """
    Gera exercícios de revisão sobre um tópico com base nos materiais.

    Args:
        topico: tópico para geração dos exercícios.
        vectorstore: índice FAISS.
        llm_fn: função de geração de texto.
        quantidade: número de exercícios.

    Returns:
        String com os exercícios gerados.
    """
    chunks = recuperar(topico, vectorstore)
    contexto = "\n\n".join(c["texto"] for c in chunks)

    messages = [
        {
            "role": "system",
            "content": "Você é um professor universitário especialista em elaborar exercícios pedagógicos.",
        },
        {
            "role": "user",
            "content": (
                f"Com base no contexto abaixo, elabore exatamente {quantidade} exercícios "
                f"sobre o tópico '{topico}'. Numere cada exercício.\n\n"
                f"Contexto:\n{contexto}"
            ),
        },
    ]
    return llm_fn(messages)


def iniciar_quiz(topico: str, vectorstore, llm_fn) -> str:
    """
    Inicia um quiz interativo de active recall.
    Gera uma pergunta sobre o tópico e aguarda resposta do usuário.

    Returns:
        Pergunta gerada pelo sistema (a avaliação é feita após o usuário responder).
    """
    chunks = recuperar(topico, vectorstore)
    contexto = "\n\n".join(c["texto"] for c in chunks)

    messages = [
        {
            "role": "system",
            "content": "Você é um professor que aplica técnicas de active recall para revisar conteúdo.",
        },
        {
            "role": "user",
            "content": (
                f"Com base no contexto abaixo sobre '{topico}', formule UMA pergunta "
                "objetiva para testar o conhecimento do aluno. "
                "Não dê a resposta.\n\n"
                f"Contexto:\n{contexto}"
            ),
        },
    ]
    pergunta = llm_fn(messages)
    return f"🧠 Quiz — {topico}\n\n{pergunta}\n\n(Responda e eu avaliarei sua resposta!)"


def avaliar_resposta_quiz(topico: str, pergunta: str, resposta_aluno: str, vectorstore, llm_fn) -> str:
    """
    Avalia a resposta do aluno em um quiz interativo.

    Returns:
        Feedback com classificação e explicação.
    """
    chunks = recuperar(topico, vectorstore)
    contexto = "\n\n".join(c["texto"] for c in chunks)

    messages = [
        {
            "role": "system",
            "content": "Você é um professor que avalia respostas de alunos de forma pedagógica e motivadora.",
        },
        {
            "role": "user",
            "content": (
                f"Contexto sobre '{topico}':\n{contexto}\n\n"
                f"Pergunta feita ao aluno:\n{pergunta}\n\n"
                f"Resposta do aluno:\n{resposta_aluno}\n\n"
                "Classifique a resposta como: correta, parcialmente correta ou incorreta. "
                "Explique o motivo e sugira o que o aluno deve revisar, se necessário."
            ),
        },
    ]
    return llm_fn(messages)