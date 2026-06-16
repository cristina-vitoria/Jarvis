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

# Query Expansion: expande a query via LLM antes de buscar no FAISS.
# Adiciona latência de ~1 chamada LLM extra por consulta RAG.
# Recomendado: true em produção, false em testes rápidos.
RAG_QUERY_EXPANSION: bool = os.getenv("RAG_QUERY_EXPANSION", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
DOCS_DIR: Path = DATA_DIR / "docs"
AGENDA_FILE: Path = DATA_DIR / "agenda.json"
TAREFAS_FILE: Path = DATA_DIR / "tarefas.json"
LOGS_DIR: Path = Path(os.getenv("LOGS_DIR", "logs"))
