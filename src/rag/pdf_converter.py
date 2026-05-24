"""Lógica centralizada de conversão PDF → Markdown + sidecar .metadata.json.

Este módulo é a ÚNICA fonte para extração e limpeza de PDFs.

Responsabilidades:
  1. Extrair texto bruto de cada página usando PyMuPDF (fitz)
  2. Limpar artefatos comuns de PDF (números de página soltos, linhas em branco excessivas)
  3. Salvar o resultado como <stem>.md em out_dir
  4. Salvar um sidecar <stem>.metadata.json no mesmo out_dir

NÃO faz chunking, embedding nem indexação — essas etapas ficam em
  src/rag/chunker.py, src/rag/embeddings.py, src/rag/vectorstore.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyMuPDF não está instalado.\n"
        "Execute: pip install pymupdf"
    ) from exc


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _extract_text(pdf_path: Path) -> str:
    """Retorna texto puro de todas as páginas usando extração layout-aware do PyMuPDF."""
    doc = fitz.open(str(pdf_path))
    pages: list[str] = []
    for page in doc:
        text = page.get_text("text")  # preserva ordem de leitura
        if text.strip():
            pages.append(text)
    doc.close()
    return "\n\n".join(pages)


def _clean_text(raw: str) -> str:
    """Remove ruídos comuns de PDF que degradam a qualidade dos embeddings."""
    # remove linhas que contêm apenas um número de página (dígitos isolados)
    raw = re.sub(r"(?m)^\s*\d{1,3}\s*$", "", raw)
    # colapsa 3+ linhas em branco consecutivas em uma única
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def _title_from_stem(stem: str) -> str:
    """Transforma o nome do arquivo em título legível."""
    return stem.replace("_", " ").replace("-", " ").title()


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def converter_pdf(
    pdf_path: Path,
    out_dir: Path,
    disciplina: str = "",
    fonte: str = "",
    fonte_url: str = "",
    licenca: str = "",
) -> tuple[Path, Path]:
    """
    Extrai, limpa e persiste um PDF como .md + sidecar .metadata.json.

    Parâmetros
    ----------
    pdf_path  : caminho para o PDF de origem
    out_dir   : pasta onde os arquivos de saída serão gravados
    disciplina: nome da disciplina (opcional, para metadados)
    fonte     : descrição da fonte (opcional, para metadados)
    fonte_url : URL da fonte original (opcional, para metadados)
    licenca   : licença do documento (opcional, para metadados)

    Retorna
    -------
    (md_path, meta_path) — caminhos dos arquivos gerados

    Levanta
    -------
    ValueError  se nenhum texto pôde ser extraído do PDF
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = _extract_text(pdf_path)
    if not raw.strip():
        raise ValueError(f"Nenhum texto pôde ser extraído de '{pdf_path.name}'.")

    text = _clean_text(raw)
    title = _title_from_stem(pdf_path.stem)

    # --- .md ---
    md_path = out_dir / f"{pdf_path.stem}.md"
    md_path.write_text(f"# {title}\n\n{text}", encoding="utf-8")

    # --- .metadata.json ---
    metadata: dict[str, str] = {
        "title": title,
        "source_pdf": pdf_path.name,
        "markdown_file": md_path.name,
        "parser": "PyMuPDF (fitz)",
        "note": "Chunking tratado por src/rag/chunker.py",
    }
    if disciplina:
        metadata["disciplina"] = disciplina
    if fonte:
        metadata["fonte"] = fonte
    if fonte_url:
        metadata["fonte_url"] = fonte_url
    if licenca:
        metadata["licenca"] = licenca

    meta_path = out_dir / f"{pdf_path.stem}.metadata.json"
    meta_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return md_path, meta_path