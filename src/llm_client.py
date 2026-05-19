"""Cliente de integração com o modelo Gemma 12B via API compatível com OpenAI."""

import json
import re
from openai import OpenAI
from src.config import LLM_BASE_URL, LLM_API_KEY, MODEL_ID, MAX_NEW_TOKENS, LLM_TIMEOUT

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Retorna (ou cria) o cliente OpenAI com timeout configurado."""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
            timeout=LLM_TIMEOUT,      # usa valor de config.py (padrão: 120s)
            max_retries=1,             # 1 retry automático antes de lançar excepção
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
# ROTEADOR DETERMINÍSTICO DE FERRAMENTAS
# ---------------------------------------------------------------------------
# Decide qual ferramenta chamar com base em palavras-chave e padrões regex.
# NÃO faz chamada ao LLM — zero latência, zero timeout.
#
# Ordem das regras: mais específica primeiro para evitar falsos positivos.
# ---------------------------------------------------------------------------

# Padrões para extração de período de agenda
_RE_AMANHA   = re.compile(r"amanhã|amanha", re.I)
_RE_SEMANA   = re.compile(r"semana|semanais|essa semana|esta semana", re.I)
_RE_HOJE     = re.compile(r"\bhoje\b|agora", re.I)

# Extração de ID numérico para concluir_tarefa
_RE_ID_TAREFA = re.compile(r"(?:tarefa|id|número|numero|#)\s*[:\-]?\s*(\d+)", re.I)
_RE_NUM_SOLO  = re.compile(r"\b(\d+)\b")


def _extrair_topico(msg: str, ancora: str) -> str:
    """Extrai o tópico removendo a âncora e palavras auxiliares."""
    idx = msg.lower().find(ancora.lower())
    if idx != -1:
        trecho = msg[idx + len(ancora):].strip()
    else:
        trecho = msg
    trecho = re.sub(r"^(sobre|acerca de|de|do|da|dos|das|para|com)\s+", "", trecho, flags=re.I)
    return trecho.rstrip("?.!").strip() or msg.strip()


def _extrair_num_perguntas(msg: str) -> int:
    """Tenta extrair quantidade de perguntas/exercícios da mensagem."""
    m = re.search(r"(\d+)\s*(?:perguntas?|questões?|questoes?|exercícios?|exercicios?)", msg, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"\b([2-9]|1\d)\b", msg)  # números 2-19 soltos
    if m:
        return int(m.group(1))
    return 3


def decidir_ferramenta(user_message: str, tools_schema: list) -> dict | None:
    """
    Decide qual ferramenta chamar de forma TOTALMENTE DETERMINÍSTICA
    (sem chamada ao LLM). Usa regex e palavras-chave.

    Returns:
        dict com {'name': str, 'arguments': dict} ou None.
    """
    msg = user_message.strip()
    low = msg.lower()

    # ------------------------------------------------------------------
    # 1. CONCLUIR TAREFA — deve vir antes de listar/adicionar
    # ------------------------------------------------------------------
    if re.search(r"conclu|marcar? como (feita?|conclu|pronta?)|finaliz|terminar?|completar?", low):
        m = _RE_ID_TAREFA.search(msg) or _RE_NUM_SOLO.search(msg)
        if m:
            return {"name": "concluir_tarefa", "arguments": {"id_tarefa": int(m.group(1))}}
        # pediu concluir mas sem ID — cai para conversa
        return None

    # ------------------------------------------------------------------
    # 2. ADICIONAR TAREFA
    # ------------------------------------------------------------------
    if re.search(r"adicionar?|criar?|nova? tarefa|incluir?|cadastrar?", low) and \
       re.search(r"tarefa|afazer|a fazer|atividade|trabalho|lembrete", low):
        # Extrai título: tudo após "tarefa", "adicionar", etc.
        titulo = re.sub(
            r"^.*(adicionar?|criar?|nova?|incluir?|cadastrar?)\s*(tarefa|atividade)?\s*[:\-]?\s*",
            "", msg, flags=re.I
        ).rstrip("?.!").strip()
        if not titulo:
            titulo = msg
        # Extrai prazo se houver
        m_prazo = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", msg)
        args: dict = {"titulo": titulo}
        if m_prazo:
            args["prazo"] = m_prazo.group(1).replace("/", "-")
        return {"name": "adicionar_tarefa", "arguments": args}

    # ------------------------------------------------------------------
    # 3. QUIZ INTERATIVO
    # ------------------------------------------------------------------
    if re.search(r"\bquiz\b|quizz|teste interativo|perguntas? interativas?", low):
        ancora = "quiz" if "quiz" in low else "teste"
        topico = _extrair_topico(msg, ancora)
        num = _extrair_num_perguntas(msg)
        return {"name": "quiz_interativo",
                "arguments": {"topico": topico, "num_perguntas": num}}

    # ------------------------------------------------------------------
    # 4. GERAR EXERCÍCIOS
    # ------------------------------------------------------------------
    if re.search(r"exercícios?|exercicios?|questões?|questoes?|gere?\s+\d*\s*exerc|criar?\s+exerc", low):
        ancora = "exercício" if "exercício" in low else "exercicio"
        topico = _extrair_topico(msg, ancora)
        num = _extrair_num_perguntas(msg)
        return {"name": "gerar_exercicios",
                "arguments": {"topico": topico, "quantidade": num}}

    # ------------------------------------------------------------------
    # 5. AGENDA
    # ------------------------------------------------------------------
    if re.search(
        r"agenda|compromisso|aula|prova|horário|horario|calendário|calendario"
        r"|o que tenho|tenho hoje|tenho amanhã|tenho amanha|esta semana|essa semana"
        r"|evento|semestre",
        low
    ):
        if _RE_AMANHA.search(low):
            periodo = "amanha"
        elif _RE_SEMANA.search(low):
            periodo = "semana"
        else:
            periodo = "hoje"
        # Verifica se há data explícita (YYYY-MM-DD)
        m_data = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", msg)
        if m_data:
            return {"name": "consultar_agenda",
                    "arguments": {"data": m_data.group(1).replace("/", "-")}}
        return {"name": "consultar_agenda", "arguments": {"periodo": periodo}}

    # ------------------------------------------------------------------
    # 6. LISTAR TAREFAS
    # ------------------------------------------------------------------
    if re.search(r"tarefas?|afazeres?|a fazer|pendentes?|atividades?", low):
        if re.search(r"concluída|concluida|feita|finalizada|completa", low):
            return {"name": "listar_tarefas", "arguments": {"status": "concluida"}}
        return {"name": "listar_tarefas", "arguments": {"status": "pendente"}}

    # ------------------------------------------------------------------
    # 7. BUSCA RAG — perguntas acadêmicas sobre conteúdo
    # ------------------------------------------------------------------
    if re.search(
        r"explique?|explica|o que é|o que são|como funciona|como são|defina|definição"
        r"|resumo?|resuma|conceitue?|descreva|descreve|fale sobre|me fale"
        r"|diferença entre|diferença entre|compare|compara|vantagens?|desvantagens?"
        r"|quais são|quais os|quando usar|para que serve|como se usa"
        r"|material|conteúdo|aula|disciplina|documento",
        low
    ):
        return {"name": "buscar_material_rag", "arguments": {"pergunta": msg}}

    # ------------------------------------------------------------------
    # 8. Conversa genérica — sem ferramenta
    # ------------------------------------------------------------------
    return None