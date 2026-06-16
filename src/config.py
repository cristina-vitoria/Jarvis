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
# Recomendado: false só em testes rápidos.
RAG_QUERY_EXPANSION: bool = os.getenv("RAG_QUERY_EXPANSION", "true").lower() == "true"

# Busca Híbrida: número de candidatos buscados antes da fusão RRF.
# N_DENSE: candidatos do FAISS (semântico)
# N_SPARSE: candidatos do BM25 (léxico)
# O resultado final é sempre RAG_TOP_K após a fusão.
RAG_HYBRID_ENABLED: bool = os.getenv("RAG_HYBRID_ENABLED", "true").lower() == "true"
RAG_HYBRID_N_DENSE: int = int(os.getenv("RAG_HYBRID_N_DENSE", "10"))
RAG_HYBRID_N_SPARSE: int = int(os.getenv("RAG_HYBRID_N_SPARSE", "10"))

# Re-ranking com Cross-Encoder.
# RAG_RERANKER_CANDIDATES: quantos candidatos buscar no FAISS antes de rerankar.
# O resultado final sempre terá RAG_TOP_K chunks.
RAG_RERANKER: bool = os.getenv("RAG_RERANKER", "true").lower() == "true"
RAG_RERANKER_CANDIDATES: int = int(os.getenv("RAG_RERANKER_CANDIDATES", "15"))


# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
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

# Prompt do sistema
SYSTEM_PROMPT = """
Você é o JARVIS Acadêmico, um assistente inteligente focado em otimizar a rotina e o aprendizado de estudantes de Ciência da Computação.

### DIRETRIZES DE COMPORTAMENTO
- Personalidade: Seja prestativo, claro, objetivo e motivador.
- Papel: Seu papel é ajudar com estudos, agenda, tarefas e revisão de conteúdo.
- Formatação de Saída: Sempre que apresentar exemplos de código, comandos de terminal, arquivos de configuração ou logs de erro, utilize blocos de código em Markdown, especificando a linguagem correta (ex: ```python, 
```bash, ```json).

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
