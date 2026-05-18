"""Geração de embeddings com Sentence Transformers."""

import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import EMBED_MODEL

_embed_model = None


def _carregar_modelo():
    global _embed_model
    if _embed_model is None:
        print(f"[Embeddings] Carregando modelo de embeddings: {EMBED_MODEL}")
        _embed_model = SentenceTransformer(EMBED_MODEL)
    return _embed_model


def gerar_embeddings(textos: list[str]) -> np.ndarray:
    """Gera embeddings normalizados para uma lista de textos."""
    modelo = _carregar_modelo()
    embeddings = modelo.encode(
        textos,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return embeddings.astype(np.float32)


def gerar_embedding_query(texto: str) -> np.ndarray:
    """Gera embedding para uma query."""
    modelo = _carregar_modelo()
    emb = modelo.encode([texto], convert_to_numpy=True, normalize_embeddings=True)
    return emb.astype(np.float32)