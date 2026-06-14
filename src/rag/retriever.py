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
        Lista de dicts com os campos do chunk indexado mais 'score'.
        Campos garantidos: 'id', 'texto', 'fonte', 'estrategia_chunking', 'score'.
        Campos opcionais (presentes quando chunking semântico foi usado):
            'heading_secao'      : título da seção Markdown de origem.
        Campos opcionais (presentes quando o pdf_converter enriqueceu o doc):
            'doc_id', 'title', 'topicos_detectados', 'disciplina'.
    """
    return vectorstore.buscar(pergunta, k=k)
