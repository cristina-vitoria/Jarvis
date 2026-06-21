"""Backfill de documentos recuperados na avaliação já realizada.

Preenche o campo `documentos_recuperados` (e corrige `tipo`) em
evaluation/resultados.json SEM alterar as respostas nem as classificações
já atribuídas por avaliador humano.

Para cada pergunta de tipo 'rag'/'aprendizado', reexecuta o mesmo pipeline
de recuperação usado pelo agente (Query Expansion/HyDE + busca híbrida +
re-ranking) e registra os chunks recuperados para rastreabilidade.

Uso:
    python evaluation/preencher_documentos.py
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from main import inicializar_rag
from src.rag.retriever import recuperar
from src.llm_client import gerar_resposta

PERGUNTAS_PATH = ROOT / "evaluation" / "perguntas.json"
RESULTADOS_PATH = ROOT / "evaluation" / "resultados.json"


def _docs_para_pergunta(pergunta, vectorstore, bm25):
    chunks = recuperar(
        pergunta,
        vectorstore,
        llm_fn=lambda msg, **kw: gerar_resposta(msg, **kw),
        bm25_store=bm25,
    )
    docs = []
    for c in chunks:
        entrada = {
            "id": c["id"],
            "fonte": c.get("fonte", ""),
            "score": round(c.get("score", 0.0), 4),
            "estrategia_chunking": c.get("estrategia_chunking", "desconhecido"),
        }
        heading = c.get("heading_secao", "").strip()
        if heading:
            entrada["heading_secao"] = heading
        docs.append(entrada)
    return docs


def main():
    resultados = json.loads(RESULTADOS_PATH.read_text(encoding="utf-8"))
    perguntas = json.loads(PERGUNTAS_PATH.read_text(encoding="utf-8"))
    tipo_por_id = {p["id"]: p.get("tipo", "rag") for p in perguntas}

    print("Inicializando RAG...")
    vectorstore, bm25 = inicializar_rag()
    if vectorstore is None:
        print("[ERRO] RAG indisponível — verifique data/docsmd/.")
        sys.exit(1)

    for r in resultados:
        pid = r["id"]
        # Corrige o tipo a partir de perguntas.json (fonte da verdade)
        r["tipo"] = tipo_por_id.get(pid, r.get("tipo", "rag"))

        if r["tipo"] in ("rag", "aprendizado"):
            print(f"[{pid}] Recuperando documentos...")
            try:
                r["documentos_recuperados"] = _docs_para_pergunta(
                    r["pergunta"], vectorstore, bm25
                )
            except Exception as exc:  # noqa: BLE001
                print(f"  Falha ao recuperar para #{pid}: {exc}")

        # Salva incrementalmente
        RESULTADOS_PATH.write_text(
            json.dumps(resultados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    preenchidos = sum(1 for r in resultados if r["documentos_recuperados"])
    print(f"\nConcluído. {preenchidos}/{len(resultados)} registros com documentos recuperados.")
    print(f"Respostas e classificações originais preservadas em: {RESULTADOS_PATH}")


if __name__ == "__main__":
    main()
