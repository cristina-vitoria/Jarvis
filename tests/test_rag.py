"""Testes básicos para o pipeline RAG."""

import pytest
from src.rag.chunker import chunk_texto, chunk_documentos


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


def test_chunk_documentos():
    """Deve gerar chunks com campos id, texto e fonte."""
    docs = [{"nome": "doc1.txt", "texto": "a" * 1500}]
    chunks = chunk_documentos(docs)
    assert len(chunks) > 0
    for c in chunks:
        assert "id" in c
        assert "texto" in c
        assert "fonte" in c
        assert c["fonte"] == "doc1.txt"


def test_chunk_overlap():
    """O overlap deve garantir que partes do texto aparecem em chunks consecutivos."""
    texto = "ABCDE" * 200  # 1000 chars
    chunks = chunk_texto(texto, chunk_size=300, overlap=100)
    if len(chunks) >= 2:
        # Parte final do chunk 0 deve estar no início do chunk 1
        fim_chunk0 = chunks[0][-100:]
        inicio_chunk1 = chunks[1][:100]
        assert fim_chunk0 == inicio_chunk1