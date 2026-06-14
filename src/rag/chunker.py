"""Divisão de documentos em chunks para indexação no RAG.

Estratégia de chunking (em ordem de prioridade):

1. **Semântico por headings** (padrão, ``usar_headings=True``)
   O ``pdf_converter`` já detecta hierarquia de títulos via tamanho de
   fonte e os salva como ``# Heading`` / ``## Heading`` no Markdown.
   Cada seção delimitada por esses headings vira um chunk independente.
   Se a seção for maior que ``CHUNK_SIZE``, ela é subdividida com overlap
   para não perder contexto entre passagens longas.
   Cada chunk carrega o campo ``heading_secao`` com o título da seção,
   de modo que o retriever pode exibir de qual parte do documento veio.

2. **Fallback por tamanho fixo** (``usar_headings=False`` ou sem headings)
   Comportamento original: janela deslizante de ``CHUNK_SIZE`` caracteres
   com sobreposição de ``CHUNK_OVERLAP``.

Cada chunk herda os metadados do documento de origem
(doc_id, title, topicos_detectados, disciplina, etc.)
"""

from __future__ import annotations

import re
from typing import Optional

from src.config import CHUNK_SIZE, CHUNK_OVERLAP

# Campos do documento que NÃO devem ser copiados para os chunks
_CAMPOS_EXCLUIDOS = frozenset(["texto", "nome"])

# Regex que identifica linhas de heading Markdown geradas pelo pdf_converter
# Captura: (marcadores '#') e (texto do heading)
_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)", re.MULTILINE)


# ---------------------------------------------------------------------------
# Chunking por tamanho fixo (fallback original)
# ---------------------------------------------------------------------------

def chunk_texto(
    texto: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Divide um texto em chunks com overlap por tamanho fixo de caracteres."""
    chunks: list[str] = []
    start = 0
    while start < len(texto):
        end = start + chunk_size
        chunk = texto[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# ---------------------------------------------------------------------------
# Chunking semântico por fronteiras de heading
# ---------------------------------------------------------------------------

def _subdividir_secao(
    heading: str,
    corpo: str,
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    """
    Subdivide o corpo de uma seção grande em sub-chunks com overlap,
    prefixando cada um com o heading para preservar contexto no retriever.

    Retorna lista de dicts com 'texto' e 'heading_secao'.
    """
    sub_chunks = chunk_texto(corpo, chunk_size, overlap)
    result: list[dict] = []
    for i, sub in enumerate(sub_chunks):
        prefixo = f"{heading}\n" if heading else ""
        sufixo = f" (parte {i + 1}/{len(sub_chunks)})" if len(sub_chunks) > 1 else ""
        result.append({
            "texto": f"{prefixo}{sub}".strip(),
            "heading_secao": f"{heading}{sufixo}".strip(),
        })
    return result


def chunk_por_headings(
    texto: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Divide o texto nas fronteiras de heading Markdown (# e ##)
    geradas pelo ``pdf_converter`` via detecção de tamanho de fonte.

    Cada elemento retornado é um dict com:
        'texto'        : conteúdo do chunk (heading + corpo)
        'heading_secao': título da seção de origem (string)

    Se o documento não possuir headings, retorna lista vazia
    (o chamador deve fazer fallback para ``chunk_texto``).

    Se uma seção individual exceder ``chunk_size``, ela é subdividida
    com overlap via ``_subdividir_secao``.
    """
    # Encontra todas as posições de heading no texto
    matches = list(_HEADING_RE.finditer(texto))

    if not matches:
        return []  # sem headings → sinaliza fallback

    secoes: list[dict] = []

    for idx, match in enumerate(matches):
        heading_texto = match.group(2).strip()
        inicio_corpo = match.end()
        # O corpo da seção vai até o próximo heading (ou fim do texto)
        fim_corpo = matches[idx + 1].start() if idx + 1 < len(matches) else len(texto)
        corpo = texto[inicio_corpo:fim_corpo].strip()

        # Ignora seções completamente vazias (ex: heading de capa sem conteúdo)
        if not corpo and not heading_texto:
            continue

        conteudo_completo = f"{match.group(0)}\n{corpo}".strip()

        if len(conteudo_completo) <= chunk_size:
            # Seção cabe em um único chunk
            secoes.append({
                "texto": conteudo_completo,
                "heading_secao": heading_texto,
            })
        else:
            # Seção grande: subdivide mantendo o heading como prefixo
            secoes.extend(
                _subdividir_secao(match.group(0), corpo, chunk_size, overlap)
            )

    return secoes


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def chunk_documentos(
    documentos: list[dict],
    usar_headings: bool = True,
) -> list[dict]:
    """
    Chunka todos os documentos propagando metadados para cada chunk.

    Parâmetros
    ----------
    documentos    : lista de dicts gerada pelo ``loader.carregar_documentos``
    usar_headings : se True (padrão), tenta chunking semântico por headings
                    antes de recorrer ao fallback por tamanho fixo

    Cada chunk retornado contém:
        'id'                 : identificador único  (ex: aula1_chunk0)
        'texto'              : conteúdo do chunk
        'fonte'              : nome do arquivo .md  (ex: aula1.md)
        'heading_secao'      : título da seção de origem (somente chunking semântico)
        'estrategia_chunking': 'heading' | 'fixo'
        + todos os campos extras do documento
          (doc_id, title, topicos_detectados, disciplina, etc.)

    Returns
    -------
    Lista de dicts.
    """
    todos_chunks: list[dict] = []

    for doc in documentos:
        prefixo = doc.get("doc_id") or doc["nome"].rsplit(".", 1)[0]
        extras = {k: v for k, v in doc.items() if k not in _CAMPOS_EXCLUIDOS}

        chunks_info: list[dict]  # lista de {'texto': ..., 'heading_secao': ...}
        estrategia: str

        if usar_headings:
            semanticos = chunk_por_headings(doc["texto"])
            if semanticos:
                chunks_info = semanticos
                estrategia = "heading"
            else:
                # Fallback: documento sem headings (OCR puro, texto simples)
                chunks_info = [
                    {"texto": t, "heading_secao": ""}
                    for t in chunk_texto(doc["texto"])
                ]
                estrategia = "fixo"
                print(
                    f"[Chunker] '{doc['nome']}': sem headings detectados "
                    "— usando chunking por tamanho fixo."
                )
        else:
            chunks_info = [
                {"texto": t, "heading_secao": ""}
                for t in chunk_texto(doc["texto"])
            ]
            estrategia = "fixo"

        for i, info in enumerate(chunks_info):
            entrada: dict = {
                "id": f"{prefixo}_chunk{i}",
                "texto": info["texto"],
                "fonte": doc["nome"],
                "estrategia_chunking": estrategia,
            }
            if info.get("heading_secao"):
                entrada["heading_secao"] = info["heading_secao"]
            entrada.update(extras)
            todos_chunks.append(entrada)

        print(
            f"[Chunker] '{doc['nome']}': {len(chunks_info)} chunks "
            f"(estratégia={estrategia})"
        )

    print(f"[Chunker] Total de chunks gerados: {len(todos_chunks)}")
    return todos_chunks
