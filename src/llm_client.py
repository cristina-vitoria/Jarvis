"""Cliente de integração com o modelo Gemma 12B via API compatível com OpenAI."""

import json
import re
import os
from openai import OpenAI
from src.config import LLM_BASE_URL, LLM_API_KEY, MODEL_ID, MAX_NEW_TOKENS, SYSTEM_PROMPT

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Retorna (ou cria) o cliente OpenAI configurado com a base_url do professor."""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
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
    Agente Revisor (Self-Correction): verifica em background se a resposta gerada
    de fato responde à pergunta usando apenas o contexto fornecido.

    Returns:
        True  → resposta aprovada (SIM).
        False → resposta reprovada (NAO), deve ser regerada.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "Você é um revisor rigoroso de respostas de sistemas RAG. "
                "Analise se a resposta gerada responde à pergunta do usuário "
                "usando APENAS informações do contexto fornecido. "
                "Responda SOMENTE com a palavra SIM ou NAO, sem explicações."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Contexto fornecido ao sistema:\n{contexto}\n\n"
                f"Pergunta do usuário:\n{pergunta}\n\n"
                f"Resposta gerada:\n{resposta}\n\n"
                "A resposta gerada responde de fato à pergunta do usuário "
                "usando apenas o contexto fornecido? Responda SIM ou NAO."
            ),
        },
    ]
    try:
        veredicto = gerar_resposta(messages, max_new_tokens=16).strip().upper()
        return veredicto.startswith("SIM")
    except Exception:
        # Em caso de falha do revisor, aprova a resposta para não bloquear o fluxo
        return True


def decidir_ferramenta(user_message: str, tools_schema: list) -> dict | None:
    """
    Pede para o modelo decidir qual ferramenta chamar (se houver).

    Returns:
        dict com {'name': str, 'arguments': dict} ou None se não houver chamada.
    """
    tools_desc = json.dumps(tools_schema, ensure_ascii=False, indent=2)
    messages = [
        {
            "role": "system",
            "content": (
                SYSTEM_PROMPT
                + "\n\nFerramentas disponíveis (JSON):\n"
                + tools_desc
                + "\n\nSe o contexto exigir o uso de uma ferramenta, responda EXCLUSIVAMENTE com um objeto JSON válido, sem marcação markdown e sem texto antes ou depois, neste formato exato:\n"
                + '{"tool": "nome_da_ferramenta", "arguments": {"arg1": "valor1"}}'
                + "\nSe não precisar de ferramenta, responda normalmente em texto."
            ),
        },
        {"role": "user", "content": user_message},
    ]
    resposta = gerar_resposta(messages, max_new_tokens=256)

    match = re.search(r'\{\s*"tool"\s*:', resposta)
    if match:
        try:
            json_str = resposta[match.start():]
            decoder = json.JSONDecoder()
            obj, _ = decoder.raw_decode(json_str)
            if "tool" in obj and "arguments" in obj:
                return {"name": obj["tool"], "arguments": obj["arguments"]}
        except (json.JSONDecodeError, KeyError):
            pass
    return None