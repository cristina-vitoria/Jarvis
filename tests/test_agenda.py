"""Testes básicos para a ferramenta de agenda."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch


AGENDA_SAMPLE = [
    {"id": 1, "data": "2099-01-01", "hora": "10:00", "tipo": "prova", "disciplina": "IA", "descricao": "Prova final"}
]


@patch("src.tools.agenda.AGENDA_PATH")
def test_consultar_agenda_hoje_sem_eventos(mock_path, tmp_path):
    """Deve retornar mensagem de nenhum evento quando não há compromissos."""
    arquivo = tmp_path / "agenda.json"
    arquivo.write_text(json.dumps([]), encoding="utf-8")
    mock_path.__bool__ = lambda self: True
    mock_path.exists.return_value = True
    mock_path.read_text.return_value = json.dumps([])

    from src.tools.agenda import consultar_agenda
    resultado = consultar_agenda(periodo="hoje")
    assert "Nenhum compromisso" in resultado


def test_consultar_agenda_retorna_string():
    """A função deve retornar sempre uma string."""
    from src.tools.agenda import consultar_agenda
    resultado = consultar_agenda(periodo="hoje")
    assert isinstance(resultado, str)