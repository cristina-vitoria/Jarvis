"""Módulo de log de chamadas de ferramentas."""

import json
from datetime import datetime
from src.config import TOOL_LOG_PATH


def log_tool_call(tool_name: str, tool_input: dict, tool_output):
    """Registra uma chamada de ferramenta no arquivo de log JSONL."""
    TOOL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "input": tool_input,
        "output": tool_output if isinstance(tool_output, (str, list, dict)) else str(tool_output),
    }
    with open(TOOL_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def ler_logs(n_ultimos: int = 20) -> list:
    """Retorna os últimos N registros de log."""
    if not TOOL_LOG_PATH.exists():
        return []
    linhas = TOOL_LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
    registros = [json.loads(l) for l in linhas if l.strip()]
    return registros[-n_ultimos:]