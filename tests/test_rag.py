"""Testes básicos para o pipeline RAG."""

import pytest
from src.rag.chunker import chunk_texto, chunk_por_headings, chunk_documentos


# ---------------------------------------------------------------------------
# chunk_texto (fallback original)
# ---------------------------------------------------------------------------

def test_chunk_texto_basico():
    """Deve dividir um texto longo em múltiplos chunks."""
    texto = "a" * 2000
    chunks = chunk_texto(texto, chunk_size=500, overlap=100)
    assert len(chunks) > 1
    assert all(len(c) <= 500 for c in chunks)


def test_chunk_texto_curto():
    """Um texto menor que chunk_size deve gerar exatamente 1 chunk."""
    texto = "Texto curto"
    chunks = chunk_texto(texto, chunk_size=500, overlap=100)
    assert len(chunks) == 1
    assert chunks[0] == "Texto curto"


def test_chunk_overlap():
    """O overlap deve garantir que partes do texto aparecem em chunks consecutivos."""
    texto = "ABCDE" * 200  # 1000 chars
    chunks = chunk_texto(texto, chunk_size=300, overlap=100)
    if len(chunks) >= 2:
        fim_chunk0 = chunks[0][-100:]
        inicio_chunk1 = chunks[1][:100]
        assert fim_chunk0 == inicio_chunk1


# ---------------------------------------------------------------------------
# chunk_por_headings
# ---------------------------------------------------------------------------

TEXTO_COM_HEADINGS = """
# Introdução
Este é o conteúdo introdutório do documento.

## Conceitos Básicos
Aqui explicamos os conceitos fundamentais.

## Aplicações
Exemplos práticos e casos de uso.

# Conclusão
Consideracões finais do documento.
""".strip()


def test_chunk_por_headings_retorna_lista():
    """Deve retornar uma lista de dicts com 'texto' e 'heading_secao'."""
    chunks = chunk_por_headings(TEXTO_COM_HEADINGS)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    for c in chunks:
        assert "texto" in c
        assert "heading_secao" in c


def test_chunk_por_headings_preserva_headings():
    """Cada chunk deve conter o heading da seção de origem."""
    chunks = chunk_por_headings(TEXTO_COM_HEADINGS)
    headings = [c["heading_secao"] for c in chunks]
    assert "Introdução" in headings
    assert "Conceitos Básicos" in headings
    assert "Conclusão" in headings


def test_chunk_por_headings_sem_headings_retorna_vazio():
    """Texto sem headings deve retornar lista vazia (sinaliza fallback)."""
    texto_sem_heading = "Apenas texto corrido sem nenhum heading markdown."
    resultado = chunk_por_headings(texto_sem_heading)
    assert resultado == []


def test_chunk_por_headings_secao_grande_subdivide():
    """Uma seção maior que chunk_size deve ser subdividida."""
    corpo_grande = "palavra " * 200  # ~1600 chars
    texto = f"# Seção Grande\n{corpo_grande}"
    chunks = chunk_por_headings(texto, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    # Todos os sub-chunks devem referenciar a mesma seção
    assert all("Seção Grande" in c["heading_secao"] for c in chunks)


def test_chunk_por_headings_texto_incluido_no_chunk():
    """O conteúdo da seção deve estar presente no texto do chunk."""
    chunks = chunk_por_headings(TEXTO_COM_HEADINGS)
    textos = " ".join(c["texto"] for c in chunks)
    assert "conceitos fundamentais" in textos
    assert "Exemplos práticos" in textos


# ---------------------------------------------------------------------------
# chunk_documentos (API pública integrada)
# ---------------------------------------------------------------------------

def test_chunk_documentos_com_headings():
    """chunk_documentos com usar_headings=True deve usar estrategia='heading'."""
    docs = [{"nome": "aula1.md", "texto": TEXTO_COM_HEADINGS}]
    chunks = chunk_documentos(docs, usar_headings=True)
    assert len(chunks) > 0
    assert all(c["estrategia_chunking"] == "heading" for c in chunks)
    assert all("heading_secao" in c for c in chunks)


def test_chunk_documentos_fallback_sem_headings():
    """Documento sem headings deve usar estrategia='fixo' automaticamente."""
    docs = [{"nome": "notas.md", "texto": "a" * 1500}]
    chunks = chunk_documentos(docs, usar_headings=True)
    assert len(chunks) > 0
    assert all(c["estrategia_chunking"] == "fixo" for c in chunks)


def test_chunk_documentos_campos_obrigatorios():
    """Todos os chunks devem ter id, texto, fonte e estrategia_chunking."""
    docs = [{"nome": "doc1.md", "texto": TEXTO_COM_HEADINGS}]
    chunks = chunk_documentos(docs)
    for c in chunks:
        assert "id" in c
        assert "texto" in c
        assert "fonte" in c
        assert "estrategia_chunking" in c
        assert c["fonte"] == "doc1.md"


def test_chunk_documentos_propaga_metadados():
    """Metadados extras do documento devem ser propagados para cada chunk."""
    docs = [{
        "nome": "aula5.md",
        "texto": TEXTO_COM_HEADINGS,
        "doc_id": "aula5",
        "disciplina": "Inteligência Artificial",
        "title": "Aula 5",
    }]
    chunks = chunk_documentos(docs)
    for c in chunks:
        assert c.get("doc_id") == "aula5"
        assert c.get("disciplina") == "Inteligência Artificial"
        assert c.get("title") == "Aula 5"
