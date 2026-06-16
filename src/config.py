"""Configurações centrais do JARVIS Acadêmico — carregadas via .env."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "none")
MODEL_ID: str = os.getenv("MODEL_ID", "Qwen/Qwen2.5-14B-Instruct-AWQ")
MAX_NEW_TOKENS: int = int(os.getenv("MAX_NEW_TOKENS", "512"))
LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "120"))

# ---------------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------------
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "3"))
EMBED_MODEL: str = os.getenv(
    "EMBED_MODEL", "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
)

# Busca Híbrida: número de candidatos buscados antes da fusão RRF.
# N_DENSE: candidatos do FAISS (semântico)
# N_SPARSE: candidatos do BM25 (léxico)
# O resultado final é sempre RAG_TOP_K após a fusão.
RAG_HYBRID_ENABLED: bool = os.getenv("RAG_HYBRID_ENABLED", "true").lower() == "true"
RAG_HYBRID_N_DENSE: int = int(os.getenv("RAG_HYBRID_N_DENSE", "10"))
RAG_HYBRID_N_SPARSE: int = int(os.getenv("RAG_HYBRID_N_SPARSE", "10"))

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
DOCS_DIR: Path = DATA_DIR / "docs"
AGENDA_FILE: Path = DATA_DIR / "agenda.json"
TAREFAS_FILE: Path = DATA_DIR / "tarefas.json"
LOGS_DIR: Path = Path(os.getenv("LOGS_DIR", "logs"))
