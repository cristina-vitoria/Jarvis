"""Testes básicos para as ferramentas de tarefas."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def _mock_tarefas_path(tmp_path):
    arquivo = tmp_path / "tarefas.json"
    arquivo.write_text(json.dumps([]), encoding="utf-8")
    return arquivo


def test_adicionar_tarefa(tmp_path):
    """Deve adicionar uma tarefa e retornar mensagem de confirmação."""
    arquivo = _mock_tarefas_path(tmp_path)
    with patch("src.tools.tarefas.TAREFAS_PATH", arquivo):
        from src.tools.tarefas import adicionar_tarefa
        resultado = adicionar_tarefa(titulo="Estudar embeddings")
        assert "Tarefa" in resultado
        assert "Estudar embeddings" in resultado


def test_listar_tarefas_vazia(tmp_path):
    """Deve informar que não há tarefas quando a lista está vazia."""
    arquivo = _mock_tarefas_path(tmp_path)
    with patch("src.tools.tarefas.TAREFAS_PATH", arquivo):
        from src.tools.tarefas import listar_tarefas
        resultado = listar_tarefas()
        assert "Nenhuma tarefa" in resultado


def test_concluir_tarefa_inexistente(tmp_path):
    """Deve informar que a tarefa não foi encontrada."""
    arquivo = _mock_tarefas_path(tmp_path)
    with patch("src.tools.tarefas.TAREFAS_PATH", arquivo):
        from src.tools.tarefas import concluir_tarefa
        resultado = concluir_tarefa(id_tarefa=999)
        assert "não encontrada" in resultado