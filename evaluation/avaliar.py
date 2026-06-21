"""Script de avaliação automática do JARVIS Acadêmico.

Roda as 15 perguntas de evaluation/perguntas.json,
registra as respostas e gera evaluation/resultados.json.

Uso:
    python evaluation/avaliar.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Garante que o diretório raiz está no path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from main import inicializar_rag
from src.agent import JarvisAgent
from src.rag.retriever import recuperar
from src.llm_client import gerar_resposta

PERGUNTAS_PATH = ROOT / "evaluation" / "perguntas.json"
RESULTADOS_PATH = ROOT / "evaluation" / "resultados.json"


def classificar_interativamente(pergunta: str, resposta: str) -> str:
    """Pede ao avaliador humano que classifique a resposta."""
    print("\n" + "=" * 60)
    print(f"PERGUNTA: {pergunta}")
    print("-" * 60)
    print(f"RESPOSTA:\n{resposta}")
    print("-" * 60)
    while True:
        opcao = input("Classificação [c=correta / p=parcial / i=incorreta]: ").strip().lower()
        if opcao == "c":
            return "correta"
        elif opcao == "p":
            return "parcialmente correta"
        elif opcao == "i":
            return "incorreta"
        else:
            print("Opção inválida. Digite c, p ou i.")


def main():
    print("=" * 60)
    print("  JARVIS Acadêmico — Avaliação do Sistema")
    print("=" * 60)

    # Carrega perguntas
    if not PERGUNTAS_PATH.exists():
        print(f"[ERRO] Arquivo não encontrado: {PERGUNTAS_PATH}")
        sys.exit(1)

    perguntas = json.loads(PERGUNTAS_PATH.read_text(encoding="utf-8"))
    print(f"\n{len(perguntas)} perguntas carregadas.")

    # Inicializa o sistema
    print("\nInicializando RAG e modelo...")
    vectorstore, bm25 = inicializar_rag()
    agente = JarvisAgent(vectorstore=vectorstore, bm25_store=bm25)
    print("Sistema inicializado!\n")

    resultados = []

    for item in perguntas:
        pid = item["id"]
        pergunta = item["pergunta"]
        tipo = item.get("tipo", "desconhecido")

        print(f"\n[{pid}/{len(perguntas)}] {tipo.upper()} — Processando...")

        # Recupera documentos se for RAG ou aprendizado.
        # Registra id, fonte, heading_secao e estrategia_chunking para
        # rastreabilidade total na análise de erros do relatório.
        docs_recuperados = []
        if tipo in ("rag", "aprendizado") and vectorstore is not None:
            # Usa o mesmo pipeline do agente (Query Expansion/HyDE + busca híbrida)
            chunks = recuperar(
                pergunta,
                vectorstore,
                llm_fn=lambda msg, **kw: gerar_resposta(msg, **kw),
                bm25_store=bm25,
            )
            for c in chunks:
                entrada_doc = {
                    "id": c["id"],
                    "fonte": c.get("fonte", ""),
                    "score": round(c.get("score", 0.0), 4),
                    "estrategia_chunking": c.get("estrategia_chunking", "desconhecido"),
                }
                # Inclui heading_secao apenas quando presente (chunking semântico)
                heading = c.get("heading_secao", "").strip()
                if heading:
                    entrada_doc["heading_secao"] = heading
                docs_recuperados.append(entrada_doc)

        # Gera resposta
        try:
            resposta = agente.responder(pergunta)
        except Exception as e:
            resposta = f"[ERRO] {e}"
            print(f"  Erro ao gerar resposta: {e}")

        # Classificação
        classificacao = classificar_interativamente(pergunta, resposta)

        resultado = {
            "id": pid,
            "tipo": tipo,
            "pergunta": pergunta,
            "documentos_recuperados": docs_recuperados,
            "resposta": resposta,
            "classificacao": classificacao,
            "avaliado_em": datetime.now().isoformat(),
        }
        resultados.append(resultado)

        # Salva incrementalmente (não perde dados se o script for interrompido)
        RESULTADOS_PATH.write_text(
            json.dumps(resultados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  ✅ Salvo: {classificacao}")

    # Sumário final
    print("\n" + "=" * 60)
    print("  SUMÁRIO DA AVALIAÇÃO")
    print("=" * 60)
    from collections import Counter
    contagem = Counter(r["classificacao"] for r in resultados)
    total = len(resultados)
    for classe, qtd in sorted(contagem.items()):
        pct = qtd / total * 100
        print(f"  {classe.capitalize()}: {qtd}/{total} ({pct:.0f}%)")

    print(f"\n  Resultados salvos em: {RESULTADOS_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
