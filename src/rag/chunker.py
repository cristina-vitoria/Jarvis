"""Divisão de documentos em chunks para indexação no RAG.

Cada chunk herda os metadados do documento de origem
(doc_id, title, topicos_detectados, disciplina, etc.),
de forma que o vectorstore e as ferramentas possam exibir
informações ricas ao usuário.
"""

from src.config import CHUNK_SIZE, CHUNK_OVERLAP

# Campos do documento que NÃO devem ser copiados para os chunks
# ('texto' é muito grande; 'nome' é substituído por 'fonte')
_CAMPOS_EXCLUIDOS = frozenset(["texto", "nome"])


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
    Chunka todos os documentos propagando metadados para cada chunk.

    Cada chunk retornado contém:
        'id'    : identificador único  (ex: aula1_chunk0)
        'texto' : conteúdo do chunk
        'fonte' : nome do arquivo .md  (ex: aula1.md)
        + todos os campos extras do documento
          (doc_id, title, topicos_detectados, disciplina, etc.)

    Returns:
        Lista de dicts.
    """
    todos_chunks = []
    for doc in documentos:
        chunks = chunk_texto(doc["texto"])

        # Prefixo do id: usa doc_id quando disponível, senão stem do nome
        prefixo = doc.get("doc_id") or doc["nome"].rsplit(".", 1)[0]

        # Metadados extras a propagar (exclui campos volumosos)
        extras = {k: v for k, v in doc.items() if k not in _CAMPOS_EXCLUIDOS}

        for i, chunk in enumerate(chunks):
            entrada: dict = {
                "id": f"{prefixo}_chunk{i}",
                "texto": chunk,
                "fonte": doc["nome"],
            }
            entrada.update(extras)  # doc_id, title, topicos_detectados, etc.
            todos_chunks.append(entrada)

    print(f"[Chunker] Total de chunks gerados: {len(todos_chunks)}")
    return todos_chunks