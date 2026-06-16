"""Query Expansion: expande a pergunta do usuário via LLM antes da busca no FAISS.

A expansão gera sinônimos e termos técnicos relacionados, aumentando a
probabilidade de o vetor da query se aproximar dos vetores dos chunks corretos.

Esta etapa é opcional e controlada por RAG_QUERY_EXPANSION=true no .env.
Se a chamada à LLM falhar, a pergunta original é usada como fallback silencioso.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_PROMPT_EXPANSAO = (
    "Você é um assistente de busca acadêmica. Sua tarefa é expandir a consulta abaixo\n"
    "Dado o trecho de pergunta abaixo, reescreva-a gerando sinônimos e termos técnicos relacionados para melhorar a recuperação de documentos.\n"
    "REGRAS ESTRITAS:\n"
    "- Retorne APENAS os termos adicionais separados por espaço.\n"
    "- NÃO inclua frases como 'Aqui estão os sinônimos', 'Termos:' ou qualquer texto de conversação.\n"
    "- NÃO repita a consulta original."
)


def expandir_query(pergunta: str, llm_fn) -> str:
    """Retorna a pergunta expandida via LLM ou a original em caso de falha.

    Args:
        pergunta: query original do usuário.
        llm_fn: callable que aceita lista de messages e retorna str.
                Normalmente `gerar_resposta` de llm_client.

    Returns:
        String com a query expandida (ou a original se a LLM falhar).
    """
    prompt = _PROMPT_EXPANSAO.format(pergunta=pergunta)
    messages = [
        {"role": "system", "content": "Você é um assistente de busca."},
        {"role": "user", "content": prompt},
    ]
    try:
        expandida = llm_fn(messages, max_new_tokens=128).strip()
        if expandida:
            logger.info("[QueryExpansion] '%s' → '%s'", pergunta, expandida)
            return expandida
    except Exception as exc:  # noqa: BLE001
        logger.warning("[QueryExpansion] Falha na expansão, usando query original: %s", exc)
    return pergunta
