"""Configurações globais do JARVIS Acadêmico."""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Caminhos
ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH / "data"
DOCS_PATH = DATA_PATH / "docs"
LOGS_PATH = ROOT_PATH / "logs"
AGENDA_PATH = DATA_PATH / "agenda.json"
TAREFAS_PATH = DATA_PATH / "tarefas.json"
TOOL_LOG_PATH = LOGS_PATH / "tool_calls.jsonl"

# Garante que as pastas existem
for p in [DATA_PATH, DOCS_PATH, LOGS_PATH]:
    p.mkdir(parents=True, exist_ok=True)

# LLM
HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_ID = os.getenv("MODEL_ID", "google/gemma-3-12b-it")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))

# RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

# Prompt do sistema
SYSTEM_PROMPT = """Você é o JARVIS Acadêmico, um assistente pessoal para estudantes.
Seu papel é ajudar com estudos, agenda, tarefas e revisão de conteúdo.
Você pode e deve chamar as ferramentas disponíveis sempre que necessário.
Quando responder sobre material acadêmico, baseie-se APENAS nos trechos recuperados.
Se a pergunta for ambígua, peça esclarecimento antes de responder.
Quando não souber a resposta, não alucine, reponda com: Não tenho informações sobre isso.
Responda sempre em português do Brasil.
"""