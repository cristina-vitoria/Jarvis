"""Ferramenta de consulta à agenda acadêmica."""

import json
from datetime import date, timedelta
from src.config import AGENDA_PATH


def _carregar_agenda() -> list:
    if not AGENDA_PATH.exists():
        return []
    return json.loads(AGENDA_PATH.read_text(encoding="utf-8"))


def consultar_agenda(data: str = None, periodo: str = None) -> str:
    """
    Consulta compromissos da agenda.

    Args:
        data: data específica no formato YYYY-MM-DD.
        periodo: 'hoje', 'amanha' ou 'semana'.

    Returns:
        String com os compromissos encontrados.
    """
    agenda = _carregar_agenda()
    hoje = date.today()

    if data:
        datas_alvo = {data}
    elif periodo == "amanha":
        datas_alvo = {(hoje + timedelta(days=1)).isoformat()}
    elif periodo == "semana":
        datas_alvo = {(hoje + timedelta(days=i)).isoformat() for i in range(7)}
    else:  # padrão: hoje
        datas_alvo = {hoje.isoformat()}

    eventos = [e for e in agenda if e.get("data") in datas_alvo]

    if not eventos:
        return f"Nenhum compromisso encontrado para o período solicitado."

    linhas = []
    for e in sorted(eventos, key=lambda x: (x.get("data", ""), x.get("hora", ""))):
        linhas.append(
            f"📅 {e.get('data')} {e.get('hora', '')} — [{e.get('tipo', '').upper()}] "
            f"{e.get('disciplina', '')} — {e.get('descricao', '')}"
        )
    return "\n".join(linhas)