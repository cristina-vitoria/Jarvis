"""Cliente de integração com o modelo Gemma 12B via API compatível com OpenAI."""

import json
import re
import threading
from openai import OpenAI
from src.config import LLM_BASE_URL, LLM_API_KEY, MODEL_ID, MAX_NEW_TOKENS, LLM_TIMEOUT

# ---------------------------------------------------------------------------
# Singleton thread-safe do cliente OpenAI
# ---------------------------------------------------------------------------
_client: OpenAI | None = None
_client_lock = threading.Lock()


def _get_client() -> OpenAI:
    """Retorna (ou cria) o cliente OpenAI com double-checked locking."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = OpenAI(
                    base_url=LLM_BASE_URL,
                    api_key=LLM_API_KEY,
                    timeout=LLM_TIMEOUT,
                    max_retries=1,
                )
    return _client


def gerar_resposta(messages: list, max_new_tokens: int = MAX_NEW_TOKENS) -> str:
    """
    Gera uma resposta textual a partir de uma lista de mensagens no formato chat.

    Args:
        messages: lista de dicts com 'role' e 'content'.
        max_new_tokens: número máximo de tokens gerados.

    Returns:
        Texto gerado pelo modelo.
    """
    client = _get_client()
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        max_tokens=max_new_tokens,
    )
    return resp.choices[0].message.content.strip()


def revisar_resposta_rag(pergunta: str, contexto: str, resposta: str) -> bool:
    """
    Agente Revisor (Self-Correction): verifica se a resposta gerada
    responde à pergunta usando apenas o contexto fornecido.

    Returns:
        True  → resposta aprovada (SIM).
        False → resposta reprovada (NAO).
    """
    messages = [
        {
            "role": "system",
            "content": (
                "Você é um revisor de respostas de sistemas RAG. "
                "Analise se a resposta gerada responde à pergunta do usuário "
                "usando APENAS informações do contexto fornecido. "
                "Responda SOMENTE com a palavra SIM ou NAO."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Contexto:\n{contexto}\n\n"
                f"Pergunta:\n{pergunta}\n\n"
                f"Resposta gerada:\n{resposta}\n\n"
                "A resposta usa apenas o contexto? SIM ou NAO."
            ),
        },
    ]
    try:
        veredicto = gerar_resposta(messages, max_new_tokens=16).strip().upper()
        return veredicto.startswith("SIM")
    except Exception:
        return True


# ---------------------------------------------------------------------------
# Parser de JSON retornado pelo LLM
# ---------------------------------------------------------------------------

def _parse_tool_json(raw: str) -> dict | None:
    """
    Extrai o primeiro objeto JSON válido de uma string — mesmo que o modelo
    embrulhe o JSON em ```json ... ``` ou adicione texto antes/depois.

    Returns:
        dict com pelo menos a chave 'tool', ou None se não encontrar.
    """
    # Tenta extrair bloco ```json ... ``` ou ``` ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.S)
    if m:
        candidate = m.group(1)
    else:
        # Tenta encontrar qualquer {...} na string
        m = re.search(r"\{.*?\}", raw, re.S)
        candidate = m.group(0) if m else raw.strip()

    try:
        data = json.loads(candidate)
        if isinstance(data, dict) and "tool" in data:
            return data
    except (json.JSONDecodeError, ValueError):
        pass
    return None


# ---------------------------------------------------------------------------
# DECISÃO PELA LLM 
# ---------------------------------------------------------------------------

# Descrições compactas enviadas ao modelo para minimizar tokens de entrada
_TOOL_DESCRIPTIONS = """Ferramentas disponíveis (use o nome exato no campo "tool"):

1. consultar_agenda      – Consulta compromissos, aulas, provas por data/período.
                           Args: {"periodo": "hoje|amanha|semana"} OU {"data": "YYYY-MM-DD"}

2. listar_tarefas        – Lista tarefas acadêmicas pendentes ou concluídas.
                           Args: {"status": "pendente|concluida"}  (status é opcional)

3. adicionar_tarefa      – Cria uma nova tarefa acadêmica.
                           Args: {"titulo": "...", "prazo": "YYYY-MM-DD"(opt), "disciplina": "..."(opt)}

4. concluir_tarefa       – Marca tarefa como concluída pelo ID numérico.
                           Args: {"id_tarefa": 7}

5. buscar_material_rag   – Busca nos materiais de estudo (PDFs/textos). Use para perguntas
                           acadêmicas: explicações, resumos, conceitos, comparações.
                           Args: {"pergunta": "..."}

6. gerar_exercicios      – Gera exercícios de revisão sobre um tópico.
                           Args: {"topico": "...", "quantidade": 3(opt)}

7. quiz_interativo       – Inicia quiz de múltipla escolha com active recall.
                           Args: {"topico": "...", "num_perguntas": 3(opt)}
"""

_SYSTEM_TOOL_SELECTOR = (
    "Você é um roteador de ferramentas para um assistente acadêmico. "
    "Analise a mensagem do usuário e decida qual ferramenta usar.\n\n"
    + _TOOL_DESCRIPTIONS
    + "\nRegras:\n"
    "- Se a mensagem se encaixa em uma ferramenta, responda APENAS com JSON válido:\n"
    '  {"tool": "nome_da_ferramenta", "args": {argumentos}}\n'
    "- Se nenhuma ferramenta se aplica (conversa genérica, saudação, etc.), responda:\n"
    '  {"tool": "nenhuma", "args": {}}\n'
    "- NÃO escreva nada além do JSON. Sem explicações, sem markdown extra."
)


def _decidir_com_llm(user_message: str) -> dict | None:
    """
    Chama o Gemma 12B para decidir qual ferramenta usar e extrair os argumentos.
    Retorna dict {'name': str, 'arguments': dict} ou None.
    """
    messages = [
        {"role": "system", "content": _SYSTEM_TOOL_SELECTOR},
        {"role": "user",   "content": user_message},
    ]
    try:
        raw = gerar_resposta(messages, max_new_tokens=128)
    except Exception as exc:
        print(f"[ToolSelector] Falha na chamada LLM: {exc}")
        return None

    parsed = _parse_tool_json(raw)
    if not parsed:
        print(f"[ToolSelector] JSON não encontrado na resposta: {raw!r}")
        return None

    tool_name = parsed.get("tool", "").strip()
    if not tool_name or tool_name.lower() in ("nenhuma", "none", "null", ""):
        return None

    args = parsed.get("args", {})
    if not isinstance(args, dict):
        args = {}

    print(f"[ToolSelector][LLM] Ferramenta escolhida: {tool_name}({args})")
    return {"name": tool_name, "arguments": args}


# ---------------------------------------------------------------------------
# PONTO DE ENTRADA PÚBLICO
# ---------------------------------------------------------------------------

def decidir_ferramenta(user_message: str, tools_schema: list) -> dict | None:
    """
    Decide qual ferramenta chamar delegando INTEIRAMENTE à LLM.
    
    Args:
        user_message: mensagem do usuário.
        tools_schema: lista de schemas das ferramentas (usada apenas para
                      compatibilidade com a assinatura anterior — a decisão
                      usa _TOOL_DESCRIPTIONS interno).

    Returns:
        dict {'name': str, 'arguments': dict} ou None.
    """

    return _decidir_com_llm(user_message)