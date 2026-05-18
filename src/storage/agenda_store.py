"""Operações de leitura e escrita na agenda acadêmica (JSON)."""

import json
from datetime import date
from src.config import AGENDA_PATH


def carregar_agenda() -> list:
    if not AGENDA_PATH.exists():
        return []
    return json.loads(AGENDA_PATH.read_text(encoding="utf-8"))


def salvar_agenda(agenda: list):
    AGENDA_PATH.write_text(json.dumps(agenda, ensure_ascii=False, indent=2), encoding="utf-8")


def adicionar_evento(data: str, hora: str, tipo: str, disciplina: str, descricao: str) -> dict:
    """Adiciona um novo evento à agenda."""
    agenda = carregar_agenda()
    novo_id = max((e["id"] for e in agenda), default=0) + 1
    evento = {
        "id": novo_id,
        "data": data,
        "hora": hora,
        "tipo": tipo,  # aula, prova, trabalho, seminario
        "disciplina": disciplina,
        "descricao": descricao,
    }
    agenda.append(evento)
    salvar_agenda(agenda)
    return evento