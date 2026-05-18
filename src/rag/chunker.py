"""Divisão de documentos em chunks para indexação no RAG."""

from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_texto(texto: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide um texto em chunks com overlap."""
    chunks = []
    start = 0
    while start < len(texto):
        end = start + chunk_size
        chunk = texto[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def chunk_documentos(documentos: list[dict]) -> list[dict]:
    """
    Chunka todos os documentos.

    Returns:
        Lista de dicts com {'id': str, 'texto': str, 'fonte': str}.
    """
    todos_chunks = []
    for doc in documentos:
        chunks = chunk_texto(doc["texto"])
        for i, chunk in enumerate(chunks):
            todos_chunks.append({
                "id": f"{doc['nome']}_chunk{i}",
                "texto": chunk,
                "fonte": doc["nome"],
            })
    print(f"[Chunker] Total de chunks gerados: {len(todos_chunks)}")
    return todos_chunks