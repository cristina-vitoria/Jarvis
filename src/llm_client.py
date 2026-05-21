"""Cliente de integração com o modelo Gemma 12B via API compatível com OpenAI."""

import json
import re
import threading
from typing import Any
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
                    max_retries=2,
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
                "Você é um revisor rigoroso de respostas de sistemas RAG. "
                "Analise se a resposta gerada responde à pergunta do usuário "
                "usando APENAS informações do contexto fornecido. "
                "Responda SOMENTE com a palavra SIM ou NAO."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Contexto fornecido ao sistem:\n{contexto}\n\n"
                f"Pergunta do usuário:\n{pergunta}\n\n"
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
# DECISÃO PELA LLM 
# ---------------------------------------------------------------------------

# Ferramentas aceitas pelo backend
_ALLOWED_TOOLS = {
    "consultar_agenda": {"periodo", "data"},
    "listar_tarefas": {"status"},
    "adicionar_tarefa": {"titulo", "prazo", "disciplina"},
    "concluir_tarefa": {"id_tarefa"},
    "buscar_material_rag": {"pergunta"},
    "gerar_exercicios": {"topico", "quantidade"},
    "quiz_interativo": {"topico", "num_perguntas"},
    "nenhuma": set(),
}

_TOOL_DESCRIPTIONS = """Ferramentas disponíveis (use o nome exato no campo "tool"):

1. consultar_agenda – Consulta compromissos, aulas, provas por data/período.
Args: {"periodo": "hoje|amanha|semana"} OU {"data": "YYYY-MM-DD"}

2. listar_tarefas – Lista tarefas acadêmicas pendentes ou concluídas.
Args: {"status": "pendente|concluida"} (status é opcional)

3. adicionar_tarefa – Cria uma nova tarefa acadêmica.
Args: {"titulo": "...", "prazo": "YYYY-MM-DD"(opt), "disciplina": "..."(opt)}

4. concluir_tarefa – Marca tarefa como concluída pelo ID numérico.
Args: {"id_tarefa": 7}

5. buscar_material_rag – Busca nos materiais de estudo (PDFs/textos).
Use para perguntas acadêmicas: explicações, resumos, conceitos, comparações.
Args: {"pergunta": "..."}

6. gerar_exercicios – Gera exercícios de revisão sobre um tópico.
Args: {"topico": "...", "quantidade": 3(opt)}

7. quiz_interativo – Inicia quiz de múltipla escolha com active recall.
Args: {"topico": "...", "num_perguntas": 3(opt)}
"""

_SYSTEM_TOOL_SELECTOR = (
    "Você é um roteador de ferramentas para um assistente acadêmico.\n"
    "Analise a mensagem do usuário e escolha NO MÁXIMO uma ferramenta.\n\n"
    f"{_TOOL_DESCRIPTIONS}\n\n"
    "Responda SOMENTE com um JSON válido seguindo EXATAMENTE este schema:\n"
    '{"tool": "nome_da_ferramenta_ou_nenhuma", "args": {}}\n\n'
    "Regras:\n"
    "- Não escreva explicações.\n"
    "- Não use markdown.\n"
    "- Se nenhuma ferramenta se aplica, use {\"tool\": \"nenhuma\", \"args\": {}}.\n"
    "- Nunca invente nomes de ferramentas.\n"
    "- Preencha apenas argumentos relevantes.\n"
)

def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None

    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def _normalize_args(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(args, dict):
        return {}

    normalized = {k: v for k, v in args.items() if k in _ALLOWED_TOOLS.get(tool_name, set())}

    if tool_name == "listar_tarefas" and "status" in normalized:
        if isinstance(normalized["status"], str):
            normalized["status"] = (
                normalized["status"]
                .strip()
                .lower()
                .replace("í", "i")
                .replace("á", "a")
            )

    if tool_name == "concluir_tarefa" and "id_tarefa" in normalized:
        try:
            normalized["id_tarefa"] = int(normalized["id_tarefa"])
        except (TypeError, ValueError):
            normalized.pop("id_tarefa", None)

    if tool_name == "gerar_exercicios" and "quantidade" in normalized:
        try:
            normalized["quantidade"] = int(normalized["quantidade"])
        except (TypeError, ValueError):
            normalized.pop("quantidade", None)

    if tool_name == "quiz_interativo" and "num_perguntas" in normalized:
        try:
            normalized["num_perguntas"] = int(normalized["num_perguntas"])
        except (TypeError, ValueError):
            normalized.pop("num_perguntas", None)

    return normalized


def _validate_tool_call(tool_name: str, args: dict[str, Any]) -> bool:
    if tool_name not in _ALLOWED_TOOLS:
        return False

    if tool_name == "consultar_agenda":
        return ("periodo" in args and isinstance(args["periodo"], str)) or (
            "data" in args and isinstance(args["data"], str)
        )

    if tool_name == "adicionar_tarefa":
        return "titulo" in args and isinstance(args["titulo"], str) and bool(args["titulo"].strip())

    if tool_name == "concluir_tarefa":
        return "id_tarefa" in args and isinstance(args["id_tarefa"], int)

    if tool_name == "buscar_material_rag":
        return "pergunta" in args and isinstance(args["pergunta"], str) and bool(args["pergunta"].strip())

    if tool_name == "gerar_exercicios":
        return "topico" in args and isinstance(args["topico"], str) and bool(args["topico"].strip())

    if tool_name == "quiz_interativo":
        return "topico" in args and isinstance(args["topico"], str) and bool(args["topico"].strip())

    return True


def decidir_ferramenta(user_message: str, tools_schema: list | None = None) -> dict | None:
    """
    Chama a LLM para decidir qual ferramenta usar.
    Retorna {'name': str, 'arguments': dict} ou None.
    """
    messages = [
        {"role": "system", "content": _SYSTEM_TOOL_SELECTOR},
        {"role": "user", "content": user_message},
    ]

    raw = None
    for attempt in range(2):
        try:
            raw = gerar_resposta(messages, max_new_tokens=128)
        except Exception as exc:
            print(f"[ToolSelector] Falha na chamada LLM: {exc}")
            return None

        parsed = _extract_json(raw)
        if parsed is not None:
            break

        messages.append({
            "role": "assistant",
            "content": raw,
        })
        messages.append({
            "role": "user",
            "content": (
                "Sua resposta anterior não estava em JSON válido. "
                "Responda novamente SOMENTE com JSON válido no formato "
                '{"tool": "nome_da_ferramenta_ou_nenhuma", "args": {}}'
            ),
        })

    if not parsed:
        print(f"[ToolSelector] JSON não encontrado na resposta: {raw!r}")
        return None

    tool_name = str(parsed.get("tool", "")).strip()
    if not tool_name or tool_name.lower() in {"nenhuma", "none", "null"}:
        return None

    args = _normalize_args(tool_name, parsed.get("args", {}))

    if not _validate_tool_call(tool_name, args):
        print(f"[ToolSelector] Chamada inválida: {tool_name}({args})")
        return None

    print(f"[ToolSelector][LLM] Ferramenta escolhida: {tool_name}({args})")
    return {"name": tool_name, "arguments": args}