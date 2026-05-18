"""Ferramentas de gerenciamento de tarefas acadêmicas."""

import json
from src.config import TAREFAS_PATH


def _carregar() -> list:
    if not TAREFAS_PATH.exists():
        return []
    return json.loads(TAREFAS_PATH.read_text(encoding="utf-8"))


def _salvar(tarefas: list):
    TAREFAS_PATH.write_text(json.dumps(tarefas, ensure_ascii=False, indent=2), encoding="utf-8")


def listar_tarefas(status: str = None) -> str:
    """Lista tarefas. Filtra por 'pendente' ou 'concluida' se informado."""
    tarefas = _carregar()
    if status:
        tarefas = [t for t in tarefas if t.get("status") == status]
    if not tarefas:
        return "Nenhuma tarefa encontrada."
    linhas = []
    for t in tarefas:
        icone = "✅" if t.get("status") == "concluida" else "📋"
        prazo = f" | Prazo: {t['prazo']}" if t.get("prazo") else ""
        disc = f" | {t['disciplina']}" if t.get("disciplina") else ""
        linhas.append(f"{icone} [{t['id']}] {t['titulo']}{disc}{prazo}")
    return "\n".join(linhas)


def adicionar_tarefa(titulo: str, prazo: str = None, disciplina: str = None) -> str:
    """Adiciona uma nova tarefa."""
    tarefas = _carregar()
    novo_id = max((t["id"] for t in tarefas), default=0) + 1
    tarefa = {
        "id": novo_id,
        "titulo": titulo,
        "prazo": prazo,
        "disciplina": disciplina,
        "status": "pendente",
    }
    tarefas.append(tarefa)
    _salvar(tarefas)
    return f"✅ Tarefa #{novo_id} adicionada: '{titulo}'."


def concluir_tarefa(id_tarefa: int) -> str:
    """Marca uma tarefa como concluída pelo ID."""
    tarefas = _carregar()
    for t in tarefas:
        if t["id"] == int(id_tarefa):
            t["status"] = "concluida"
            _salvar(tarefas)
            return f"✅ Tarefa #{id_tarefa} marcada como concluída."
    return f"Tarefa #{id_tarefa} não encontrada."