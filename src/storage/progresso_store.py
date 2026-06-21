"""Persistência do progresso de aprendizado por tópico.

Registra resultados de quizzes e expõe métricas de desempenho por tópico,
permitindo acompanhar a evolução do aluno.
"""

import json
from datetime import datetime
from src.config import PROGRESSO_PATH


def carregar_progresso() -> dict:
    if not PROGRESSO_PATH.exists():
        return {}
    try:
        return json.loads(PROGRESSO_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return {}


def salvar_progresso(progresso: dict):
    PROGRESSO_PATH.write_text(
        json.dumps(progresso, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def registrar_resultado_quiz(topico: str, acertos: int, total: int):
    """Persiste o resultado de um quiz para o tópico dado."""
    progresso = carregar_progresso()
    chave = topico.lower().strip()
    historico_anterior = progresso.get(chave, {}).get("historico", [])
    percentual = int(acertos / total * 100) if total else 0
    historico_anterior.append({
        "data": datetime.now().isoformat(),
        "acertos": acertos,
        "total": total,
        "percentual": percentual,
    })
    progresso[chave] = {
        "topico": topico,
        "ultimo_quiz": datetime.now().isoformat(),
        "acertos": acertos,
        "total": total,
        "percentual": percentual,
        "historico": historico_anterior[-10:],  # mantém últimos 10 registros
    }
    salvar_progresso(progresso)


def listar_topicos_fracos(limite: int = 5) -> list:
    """Retorna tópicos ordenados do pior para o melhor desempenho."""
    progresso = carregar_progresso()
    ordenados = sorted(progresso.values(), key=lambda x: x.get("percentual", 100))
    return ordenados[:limite]


def resumo_progresso() -> str:
    """Retorna resumo textual do progresso por tópico."""
    progresso = carregar_progresso()
    if not progresso:
        return "Nenhum quiz realizado ainda. Faça um quiz para acompanhar seu progresso!"
    linhas = ["📊 **Progresso por tópico:**\n"]
    for item in sorted(progresso.values(), key=lambda x: x.get("percentual", 0)):
        pct = item.get("percentual", 0)
        emoji = "🟢" if pct >= 80 else ("🟡" if pct >= 50 else "🔴")
        ultimo = item.get("ultimo_quiz", "")[:10]
        linhas.append(
            f"{emoji} **{item['topico']}**: {item['acertos']}/{item['total']} "
            f"({pct}%) — último quiz em {ultimo}"
        )
    return "\n".join(linhas)
