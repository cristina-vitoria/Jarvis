"""Gera um relatório formatado em Markdown com os resultados da avaliação.

Uso:
    python evaluation/gerar_relatorio.py
"""

import sys
import json
from pathlib import Path
from collections import Counter
from datetime import datetime

ROOT = Path(__file__).parent.parent
RESULTADOS_PATH = ROOT / "evaluation" / "resultados.json"
RELATORIO_PATH = ROOT / "evaluation" / "relatorio.md"


def main():
    if not RESULTADOS_PATH.exists():
        print("[ERRO] resultados.json não encontrado. Execute avaliar.py primeiro.")
        sys.exit(1)

    resultados = json.loads(RESULTADOS_PATH.read_text(encoding="utf-8"))
    total = len(resultados)
    contagem = Counter(r["classificacao"] for r in resultados)

    linhas = [
        "# Relatório de Avaliação — JARVIS Acadêmico\n",
        f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}  ",
        f"**Total de perguntas:** {total}\n",
        "## Sumário\n",
        "| Classificação | Quantidade | Percentual |",
        "|---|---|---|",
    ]
    for classe in ["correta", "parcialmente correta", "incorreta"]:
        qtd = contagem.get(classe, 0)
        pct = qtd / total * 100 if total else 0
        linhas.append(f"| {classe.capitalize()} | {qtd} | {pct:.0f}% |")

    linhas.append("\n## Resultados Detalhados\n")
    for r in resultados:
        emoji = {"correta": "✅", "parcialmente correta": "🟡", "incorreta": "❌"}.get(r["classificacao"], "❓")
        linhas.append(f"### {emoji} Pergunta {r['id']} — {r['tipo'].upper()}\n")
        linhas.append(f"**Pergunta:** {r['pergunta']}\n")
        if r["documentos_recuperados"]:
            docs = ", ".join(r["documentos_recuperados"])
            linhas.append(f"**Documentos recuperados:** `{docs}`\n")
        linhas.append(f"**Resposta:**\n\n> {r['resposta'].replace(chr(10), chr(10) + '> ')}\n")
        linhas.append(f"**Classificação:** {r['classificacao'].capitalize()}\n")
        linhas.append("---\n")

    conteudo = "\n".join(linhas)
    RELATORIO_PATH.write_text(conteudo, encoding="utf-8")
    print(f"Relatório gerado em: {RELATORIO_PATH}")


if __name__ == "__main__":
    main()