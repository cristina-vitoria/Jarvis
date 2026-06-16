"""Query Expansion e HyDE: estratégias de expansão de query antes da busca RAG.

Esta etapa é opcional e controlada por RAG_QUERY_EXPANSION=true no .env.
A estratégia é selecionada por RAG_QUERY_EXPANSION_MODE no .env:

  - 'expansion' (padrão): gera sinônimos e termos técnicos adicionais via LLM.
  - 'hyde': Hypothetical Document Embeddings — pede à LLM que gere um
    trecho de documento hipotético que responderia à pergunta. O embedding
    desse trecho aproxima mais o vetor da query dos vetores dos chunks reais,
    especialmente quando o vocabulário da pergunta difere do material.

Em ambos os modos, se a chamada à LLM falhar, a pergunta original é usada
como fallback silencioso.
"""

from __future__ import annotations

import logging

from src.config import RAG_QUERY_EXPANSION_MODE

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Modo 1: Expansão clássica de termos
# ---------------------------------------------------------------------------

_PROMPT_EXPANSAO = (
    "Você é um assistente de busca acadêmica. Sua tarefa é expandir a consulta abaixo.\n"
    "Dado o trecho de pergunta abaixo, reescreva-a gerando sinônimos e termos técnicos "
    "relacionados para melhorar a recuperação de documentos.\n"
    "REGRAS ESTRITAS:\n"
    "- Retorne APENAS os termos adicionais separados por espaço.\n"
    "- NÃO inclua frases como 'Aqui estão os sinônimos', 'Termos:' ou qualquer texto de conversação.\n"
    "- NÃO repita a consulta original.\n\n"
    "Pergunta: {pergunta}"
)


def expandir_query(pergunta: str, llm_fn) -> str:
    """Retorna a pergunta expandida com sinônimos e termos técnicos via LLM.

    Em caso de falha, retorna a pergunta original como fallback silencioso.

    Args:
        pergunta: query original do usuário.
        llm_fn: callable que aceita lista de messages e retorna str.

    Returns:
        String com os termos expandidos (ou a original se a LLM falhar).
    """
    prompt = _PROMPT_EXPANSAO.format(pergunta=pergunta)
    messages = [
        {"role": "system", "content": "Você é um assistente de busca acadêmica."},
        {"role": "user", "content": prompt},
    ]
    try:
        expandida = llm_fn(messages, max_new_tokens=128).strip()
        if expandida:
            logger.info("[QueryExpansion] '%s' → '%s'", pergunta, expandida)
            # Concatena termos expandidos à query original para não perder contexto
            return f"{pergunta} {expandida}"
    except Exception as exc:  # noqa: BLE001
        logger.warning("[QueryExpansion] Falha na expansão, usando query original: %s", exc)
    return pergunta


# ---------------------------------------------------------------------------
# Modo 2: HyDE — Hypothetical Document Embeddings
# ---------------------------------------------------------------------------

_PROMPT_HYDE = (
    "Você é um assistente acadêmico.\n"
    "Escreva um trecho de material didático (slides, apostila ou livro) que responderia "
    "diretamente à pergunta abaixo. O trecho deve:\n"
    "- Ter entre 3 e 6 frases, no estilo de um texto acadêmico.\n"
    "- Usar a terminologia técnica correta da área.\n"
    "- Conter os conceitos centrais que alguém esperaria encontrar ao responder a pergunta.\n"
    "- NÃO incluir prefixos como 'Resposta:', 'Trecho:' ou frases de abertura conversacional.\n\n"
    "Pergunta: {pergunta}"
)


def hyde_query(pergunta: str, llm_fn) -> str:
    """Gera um documento hipotético que responderia à pergunta (HyDE).

    O documento gerado é usado como query para o retriever em vez da
    pergunta original. Isso aproxima o vetor da query dos vetores dos
    chunks reais no espaço de embeddings.

    Em caso de falha, retorna a pergunta original como fallback silencioso.

    Args:
        pergunta: query original do usuário.
        llm_fn: callable que aceita lista de messages e retorna str.

    Returns:
        Documento hipotético (str) ou a pergunta original em caso de falha.
    """
    prompt = _PROMPT_HYDE.format(pergunta=pergunta)
    messages = [
        {"role": "system", "content": "Você é um assistente acadêmico de Ciência da Computação."},
        {"role": "user", "content": prompt},
    ]
    try:
        doc_hipotetico = llm_fn(messages, max_new_tokens=256).strip()
        if doc_hipotetico:
            logger.info(
                "[HyDE] Documento hipotético gerado para '%s': '%s...'",
                pergunta,
                doc_hipotetico[:80],
            )
            return doc_hipotetico
    except Exception as exc:  # noqa: BLE001
        logger.warning("[HyDE] Falha na geração do documento hipotético, usando query original: %s", exc)
    return pergunta


# ---------------------------------------------------------------------------
# Dispatcher — escolhe a estratégia com base na config
# ---------------------------------------------------------------------------

def aplicar_query_strategy(pergunta: str, llm_fn) -> str:
    """Aplica a estratégia de expansão configurada em RAG_QUERY_EXPANSION_MODE.

    Modos disponíveis:
        'expansion': gera termos adicionais (padrão histórico).
        'hyde'     : gera documento hipotético (HyDE).

    Args:
        pergunta: query original do usuário.
        llm_fn: callable de geração de texto.

    Returns:
        Query transformada (str).
    """
    modo = RAG_QUERY_EXPANSION_MODE.lower().strip()
    if modo == "hyde":
        return hyde_query(pergunta, llm_fn)
    # Padrão: expansão clássica
    return expandir_query(pergunta, llm_fn)
