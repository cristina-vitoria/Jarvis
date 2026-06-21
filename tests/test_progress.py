"""Testes para o módulo de progresso de aprendizado."""

import json
from unittest.mock import patch


def _mock_progresso_path(tmp_path):
    return tmp_path / "progresso.json"


def test_registrar_resultado_quiz(tmp_path):
    caminho = _mock_progresso_path(tmp_path)
    with patch("src.storage.progresso_store.PROGRESSO_PATH", caminho):
        from src.storage.progresso_store import registrar_resultado_quiz
        registrar_resultado_quiz("algoritmos", acertos=7, total=10)
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        assert "algoritmos" in dados
        assert dados["algoritmos"]["percentual"] == 70
        assert dados["algoritmos"]["acertos"] == 7


def test_registrar_resultado_atualiza_existente(tmp_path):
    caminho = _mock_progresso_path(tmp_path)
    with patch("src.storage.progresso_store.PROGRESSO_PATH", caminho):
        from src.storage.progresso_store import registrar_resultado_quiz
        registrar_resultado_quiz("algoritmos", acertos=4, total=10)
        registrar_resultado_quiz("algoritmos", acertos=8, total=10)
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        assert dados["algoritmos"]["percentual"] == 80
        assert len(dados["algoritmos"]["historico"]) == 2


def test_listar_topicos_fracos_ordenado(tmp_path):
    caminho = _mock_progresso_path(tmp_path)
    with patch("src.storage.progresso_store.PROGRESSO_PATH", caminho):
        from src.storage.progresso_store import registrar_resultado_quiz, listar_topicos_fracos
        registrar_resultado_quiz("ponteiros", acertos=2, total=10)   # 20%
        registrar_resultado_quiz("recursão", acertos=5, total=10)    # 50%
        registrar_resultado_quiz("arrays", acertos=9, total=10)      # 90%
        fracos = listar_topicos_fracos(limite=2)
        assert fracos[0]["topico"] == "ponteiros"
        assert fracos[1]["topico"] == "recursão"


def test_resumo_progresso_sem_dados(tmp_path):
    caminho = _mock_progresso_path(tmp_path)
    with patch("src.storage.progresso_store.PROGRESSO_PATH", caminho):
        from src.storage.progresso_store import resumo_progresso
        resultado = resumo_progresso()
        assert "Nenhum quiz" in resultado


def test_resumo_progresso_com_dados(tmp_path):
    caminho = _mock_progresso_path(tmp_path)
    with patch("src.storage.progresso_store.PROGRESSO_PATH", caminho):
        from src.storage.progresso_store import registrar_resultado_quiz, resumo_progresso
        registrar_resultado_quiz("listas", acertos=3, total=5)
        resultado = resumo_progresso()
        assert "listas" in resultado
        assert "60%" in resultado


def test_historico_limitado_a_10(tmp_path):
    caminho = _mock_progresso_path(tmp_path)
    with patch("src.storage.progresso_store.PROGRESSO_PATH", caminho):
        from src.storage.progresso_store import registrar_resultado_quiz
        for i in range(15):
            registrar_resultado_quiz("pilhas", acertos=i % 5, total=10)
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        assert len(dados["pilhas"]["historico"]) == 10
