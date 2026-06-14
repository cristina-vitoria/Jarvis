"""Configurações globais do JARVIS Acadêmico."""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Caminhos
ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH / "data"

# data/docs  — PDFs originais carregados pelo usuário (input do script de extração)
DOCS_PATH = DATA_PATH / "docs"

# data/docsmd — Markdown limpo gerado por data/scripts/extract_pdf.py
#               É A ÚNICA fonte lida pelo RAG.
DOCSMD_PATH = DATA_PATH / "docsmd"

LOGS_PATH = ROOT_PATH / "logs"
AGENDA_PATH = DATA_PATH / "agenda.json"
TAREFAS_PATH = DATA_PATH / "tarefas.json"
TOOL_LOG_PATH = LOGS_PATH / "tool_calls.jsonl"

# Garante que as pastas existem
for p in [DATA_PATH, DOCS_PATH, DOCSMD_PATH, LOGS_PATH]:
    p.mkdir(parents=True, exist_ok=True)

# LLM — API compatível com OpenAI
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen2.5-14B-Instruct-AWQ")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
# Timeout em segundos para chamadas ao LLM (aumentar se a API for lenta)
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

# RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

# Prompt do sistema
SYSTEM_PROMPT = """
Você é o JARVIS Acadêmico, um assistente inteligente focado em otimizar a rotina e o aprendizado de estudantes de Ciência da Computação.

### DIRETRIZES DE COMPORTAMENTO
1. Personalidade: Seja prestativo, claro, objetivo e motivador.
2. Papel: Seu papel é ajudar com estudos, agenda, tarefas e revisão de conteúdo.

### USO DE FERRAMENTAS (TOOL CALLING)
- Você tem acesso a ferramentas de agenda, gerenciamento de tarefas e busca de materiais acadêmicos.
- Acione as ferramentas SEMPRE que o usuário pedir para verificar horários, gerenciar atividades ou perguntar sobre o conteúdo das aulas.
- Se a solicitação do usuário for ambígua ou faltarem parâmetros, peça esclarecimentos antes de chamar a ferramenta.

### REGRAS DE CONSULTA E ESTUDO (RAG)
- Quando o usuário fizer perguntas sobre o material de estudo, acione a ferramenta de busca.
- Ao gerar a resposta, baseie-se ESTRITAMENTE e SOMENTE nos trechos recuperados pelo sistema.
- Se os trechos recuperados NÃO contiverem a resposta para a pergunta, diga explicitamente: "Não encontrei essa informação nos materiais fornecidos." 
- NUNCA invente informações ou adivinhe conceitos acadêmicos.
- Sempre mencione o nome do documento ou a origem de onde você extraiu a informação.

"""
