"""Ferramenta de planejamento de estudos.

Combina três fontes de informação para montar um plano priorizado:
  - Agenda acadêmica (compromissos da semana)
  - Lista de tarefas pendentes
  - Materiais de estudo (RAG), quando um foco/tópico é informado

A decisão final de priorização é delegada à LLM, que recebe o panorama
consolidado e devolve um plano de estudos textual.
"""

from src.tools.agenda import consultar_agenda
from src.tools.tarefas import listar_tarefas
from src.rag.retriever import recuperar


def montar_plano_estudos(
    foco: str = None,
    vectorstore=None,
    llm_fn=None,
    bm25_store=None,
) -> str:
    """Monta um plano de estudos combinando agenda, tarefas e materiais.

    Args:
        foco: tópico/prova a priorizar (opcional). Quando informado e houver
              materiais carregados, trechos relevantes são incluídos no contexto.
        vectorstore: índice FAISS (opcional, usado apenas se houver foco).
        llm_fn: função de geração de texto (obrigatória para gerar o plano).
        bm25_store: índice BM25 opcional para busca híbrida.

    Returns:
        Plano de estudos textual gerado pela LLM.
    """
    if llm_fn is None:
        return "Planejamento indisponível: modelo de linguagem não configurado."

    # --- 1. Agenda da semana ---
    agenda_semana = consultar_agenda(periodo="semana")

    # --- 2. Tarefas pendentes ---
    tarefas_pendentes = listar_tarefas(status="pendente")

    # --- 3. Materiais relevantes ao foco (opcional) ---
    contexto_material = ""
    if foco and vectorstore is not None:
        try:
            chunks = recuperar(foco, vectorstore, llm_fn=llm_fn, bm25_store=bm25_store)
            if chunks:
                contexto_material = "\n\n".join(
                    f"[{c.get('fonte', 'doc')}] {c['texto']}" for c in chunks
                )
        except Exception as exc:  # noqa: BLE001
            print(f"[planejamento] Falha ao recuperar material sobre '{foco}': {exc}")

    foco_txt = f"O aluno quer priorizar: **{foco}**.\n\n" if foco else ""
    material_txt = (
        f"=== TRECHOS DOS MATERIAIS SOBRE O FOCO ===\n{contexto_material}\n"
        f"=== FIM DOS MATERIAIS ===\n\n"
        if contexto_material
        else ""
    )

    messages = [
        {
            "role": "system",
            "content": (
                "Você é um tutor acadêmico que monta planos de estudo realistas e priorizados. "
                "Use os compromissos da agenda e as tarefas pendentes para distribuir o tempo. "
                "Destaque prazos próximos e provas. Seja objetivo e use uma lista organizada."
            ),
        },
        {
            "role": "user",
            "content": (
                f"{foco_txt}"
                f"=== AGENDA DA SEMANA ===\n{agenda_semana}\n=== FIM DA AGENDA ===\n\n"
                f"=== TAREFAS PENDENTES ===\n{tarefas_pendentes}\n=== FIM DAS TAREFAS ===\n\n"
                f"{material_txt}"
                "Com base nas informações acima, monte um plano de estudos priorizado. "
                "Indique o que estudar primeiro e por quê (prazos, provas, dependências)."
            ),
        },
    ]

    return llm_fn(messages)
