"""Operações de leitura e escrita nas tarefas acadêmicas (JSON)."""

import json
from src.config import TAREFAS_PATH


def carregar_tarefas() -> list:
    if not TAREFAS_PATH.exists():
        return []
    return json.loads(TAREFAS_PATH.read_text(encoding="utf-8"))


def salvar_tarefas(tarefas: list):
    TAREFAS_PATH.write_text(json.dumps(tarefas, ensure_ascii=False, indent=2), encoding="utf-8")