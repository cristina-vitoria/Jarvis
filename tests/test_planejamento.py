"""Testes básicos para a ferramenta de planejamento de estudos."""

from unittest.mock import patch
from src.tools.planejamento import montar_plano_estudos


def test_sem_llm_retorna_aviso():
    """Sem llm_fn configurada, deve retornar mensagem amigável (não quebrar)."""
    resultado = montar_plano_estudos(foco="provas", llm_fn=None)
    assert "indisponível" in resultado.lower()


def test_combina_agenda_e_tarefas_no_prompt():
    """O plano deve consolidar agenda da semana e tarefas pendentes no contexto da LLM."""
    capturado = {}

    def fake_llm(messages, **kwargs):
        capturado["messages"] = messages
        return "Plano gerado."

    with patch("src.tools.planejamento.consultar_agenda", return_value="AGENDA_FAKE") as ag, \
         patch("src.tools.planejamento.listar_tarefas", return_value="TAREFAS_FAKE") as tf:
        resultado = montar_plano_estudos(llm_fn=fake_llm)

    # As fontes obrigatórias foram consultadas
    ag.assert_called_once_with(periodo="semana")
    tf.assert_called_once_with(status="pendente")

    conteudo_usuario = capturado["messages"][-1]["content"]
    assert "AGENDA_FAKE" in conteudo_usuario
    assert "TAREFAS_FAKE" in conteudo_usuario
    assert resultado == "Plano gerado."
