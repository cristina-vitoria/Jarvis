"""Interface de recuperação de chunks para uso nas ferramentas."""

from src.config import RAG_TOP_K


def recuperar(pergunta: str, vectorstore, k: int = RAG_TOP_K) -> list[dict]:
    """
    Recupera os chunks mais relevantes para a pergunta.

    Args:
        pergunta: query do usuário.
        vectorstore: instância de VectorStore.
        k: número de chunks a retornar.

    Returns:
        Lista de dicts com 'id', 'texto', 'fonte' e 'score'.
    """
    return vectorstore.buscar(pergunta, k=k)