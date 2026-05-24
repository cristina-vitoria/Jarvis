"""Lógica centralizada de conversão PDF → Markdown + sidecar .metadata.json.

Este módulo é a ÚNICA fonte para extração e limpeza de PDFs.

Responsabilidades:
  1. Extrair texto de cada página usando PyMuPDF (fitz)
     - Detecta encoding corrompido (fontes Type 3 do LaTeX, scans, etc.)
     - Faz fallback automático para OCR via pytesseract quando necessário
  2. Preservar estrutura de headings via tamanho de fonte (quando disponível)
  3. Limpar artefatos comuns de PDF
  4. Salvar o resultado como <stem>.md em out_dir
  5. Salvar um sidecar <stem>.metadata.json no mesmo out_dir

NÃO faz chunking, embedding nem indexação — essas etapas ficam em
  src/rag/chunker.py, src/rag/embeddings.py, src/rag/vectorstore.py.
"""

from __future__ import annotations

import json
import re
import warnings
from datetime import datetime, timezone
from pathlib import Path
from statistics import mode
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise ImportError(
        "PyMuPDF não está instalado.\n"
        "Execute: pip install pymupdf"
    ) from exc

try:
    import pytesseract
    from PIL import Image
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Proporção mínima de caracteres ASCII imprimíveis para considerar texto válido.
# Fontes Type 3 do LaTeX geram ~35 % — bem abaixo do limiar.
_ASCII_RATIO_THRESHOLD = 0.60

# Fator de zoom para renderização de página antes do OCR (maior = melhor qualidade)
_OCR_DPI_FACTOR = 2.5

# Língua padrão para o Tesseract
_OCR_LANG = "por+eng"


# ---------------------------------------------------------------------------
# Detecção de texto corrompido
# ---------------------------------------------------------------------------

def _ascii_ratio(text: str) -> float:
    """Proporção de caracteres ASCII imprimíveis no texto (excluindo espaços/newlines)."""
    stripped = text.replace("\n", "").replace(" ", "")
    if not stripped:
        return 0.0
    printable = sum(1 for c in stripped if c.isprintable() and ord(c) < 128)
    return printable / len(stripped)


def _is_garbled(text: str) -> bool:
    """Retorna True se o texto contém encoding corrompido (Type 3 / scan sem OCR)."""
    return _ascii_ratio(text) < _ASCII_RATIO_THRESHOLD


# ---------------------------------------------------------------------------
# OCR fallback
# ---------------------------------------------------------------------------

def _ocr_page(page) -> str:
    """Renderiza a página como imagem e extrai texto via Tesseract."""
    if not _OCR_AVAILABLE:
        raise RuntimeError(
            "pytesseract e Pillow são necessários para OCR.\n"
            "Execute: pip install pytesseract pillow\n"
            "E instale o Tesseract: apt install tesseract-ocr tesseract-ocr-por"
        )
    mat = fitz.Matrix(_OCR_DPI_FACTOR, _OCR_DPI_FACTOR)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text = pytesseract.image_to_string(img, lang=_OCR_LANG)
    return text


# ---------------------------------------------------------------------------
# Extração com estrutura (headings via tamanho de fonte)
# ---------------------------------------------------------------------------

def _extract_structured_page(page) -> str:
    """
    Extrai texto de uma página preservando hierarquia de headings.

    Usa o tamanho de fonte de cada span para classificar:
      - tamanho dominante → parágrafo normal
      - tamanho > dominante + 2pt → heading Markdown (# ou ##)
    """
    data = page.get_text("dict")
    blocks = data.get("blocks", [])

    # Coleta todos os tamanhos de fonte para determinar o tamanho-corpo
    all_sizes: list[float] = []
    for b in blocks:
        if b.get("type") != 0:
            continue
        for line in b.get("lines", []):
            for span in line.get("spans", []):
                size = span.get("size", 0)
                if size > 0:
                    all_sizes.append(round(size))

    body_size: float = mode(all_sizes) if all_sizes else 11.0

    lines_out: list[str] = []
    for b in blocks:
        if b.get("type") != 0:
            continue
        for line in b.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            line_text = "".join(s.get("text", "") for s in spans).strip()
            if not line_text:
                continue
            # Tamanho representativo da linha (maior span)
            line_size = max(s.get("size", 0) for s in spans)
            if line_size >= body_size + 6:
                lines_out.append(f"# {line_text}")
            elif line_size >= body_size + 2:
                lines_out.append(f"## {line_text}")
            else:
                lines_out.append(line_text)

    return "\n".join(lines_out)


# ---------------------------------------------------------------------------
# Extração principal
# ---------------------------------------------------------------------------

def _extract_text(pdf_path: Path) -> tuple[str, bool]:
    """
    Retorna (texto_completo, usou_ocr).

    Para cada página:
      1. Tenta extração nativa com estrutura (headings via fonte)
      2. Se o resultado for corrompido, usa OCR como fallback
      3. Emite warning para páginas sem texto extraído
    """
    pages: list[str] = []
    used_ocr = False

    with fitz.open(str(pdf_path)) as doc:
        for i, page in enumerate(doc):
            page_label = f"Página {i + 1} de '{pdf_path.name}'"

            # --- tentativa 1: extração nativa estruturada ---
            native_text = _extract_structured_page(page)

            if native_text.strip() and not _is_garbled(native_text):
                pages.append(f"<!-- página {i + 1} -->\n{native_text}")
                continue

            # --- tentativa 2: OCR ---
            if _OCR_AVAILABLE:
                warnings.warn(
                    f"{page_label}: texto nativo corrompido ou ausente "
                    f"(ASCII ratio={_ascii_ratio(native_text):.0%}). "
                    "Usando OCR como fallback.",
                    UserWarning,
                    stacklevel=3,
                )
                ocr_text = _ocr_page(page).strip()
                if ocr_text:
                    used_ocr = True
                    pages.append(f"<!-- página {i + 1} [OCR] -->\n{ocr_text}")
                    continue

            # --- sem texto ---
            warnings.warn(
                f"{page_label}: nenhum texto pôde ser extraído "
                "(página pode ser imagem sem OCR disponível).",
                UserWarning,
                stacklevel=3,
            )

    return "\n\n".join(pages), used_ocr


# ---------------------------------------------------------------------------
# Limpeza
# ---------------------------------------------------------------------------

def _clean_text(raw: str) -> str:
    """Remove ruídos comuns de PDF sem apagar conteúdo legítimo."""
    # Remove linhas que contêm APENAS dígitos isolados (típico rodapé de página),
    # mas somente se estiverem entre linhas em branco — evita apagar anos ou valores.
    raw = re.sub(r"(?m)(?:^|\n)[ \t]*(\d{1,4})[ \t]*(?=\n\n|\n$|$)", "", raw)
    # Colapsa 3+ linhas em branco consecutivas em duas
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def _title_from_stem(stem: str) -> str:
    """Transforma o nome do arquivo em título legível."""
    return stem.replace("_", " ").replace("-", " ").title()


def _extract_topics(markdown: str) -> list[str]:
    """Extrai tópicos a partir de headings Markdown (# e ##) e padrões de seção do OCR.

    Padrão OCR detectado: linhas curtas que começam com dígito + ponto (e.g. '1 Organização')
    ou que estejam entre linhas em branco e não terminem com ponto.
    """
    topics: list[str] = []

    # Headings Markdown explícitos
    topics += re.findall(r"^#{1,3}\s+(.+)", markdown, re.MULTILINE)

    # Padrão OCR: "1 Título do capítulo" ou "1.2 Subtítulo"
    topics += re.findall(r"(?m)^(?:\d+[\.\d]*\s+)([A-ZÁÉÍÓÚÀÂÊÔÃÕÜÇ][^\n]{3,60})$", markdown)

    # Remove duplicatas preservando ordem
    seen: set[str] = set()
    result: list[str] = []
    for t in topics:
        t = t.strip()
        if t and t not in seen:
            seen.add(t)
            result.append(t)
    return result


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
    ocr_lang: Optional[str] = None,
) -> tuple[Path, Path]:
    """
    Extrai, limpa e persiste um PDF como .md + sidecar .metadata.json.

    Parâmetros
    ----------
    pdf_path  : caminho para o PDF de origem
    out_dir   : pasta onde os arquivos de saída serão gravados
    disciplina: nome da disciplina (opcional)
    fonte     : descrição da fonte (opcional)
    fonte_url : URL da fonte original (opcional)
    licenca   : licença do documento (opcional)
    ocr_lang  : língua(s) para o Tesseract (padrão: 'por+eng')

    Retorna
    -------
    (md_path, meta_path) — caminhos dos arquivos gerados

    Levanta
    -------
    ValueError  se nenhum texto pôde ser extraído do PDF
    """
    global _OCR_LANG
    if ocr_lang:
        _OCR_LANG = ocr_lang

    pdf_path = Path(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Conta páginas sem abrir doc duas vezes
    with fitz.open(str(pdf_path)) as _doc:
        num_pages = len(_doc)

    raw, used_ocr = _extract_text(pdf_path)

    if not raw.strip():
        raise ValueError(
            f"Nenhum texto pôde ser extraído de '{pdf_path.name}'. "
            "Verifique se o pytesseract está instalado para PDFs escaneados."
        )

    text = _clean_text(raw)
    title = _title_from_stem(pdf_path.stem)
    topics = _extract_topics(text)

    # --- .md ---
    md_path = out_dir / f"{pdf_path.stem}.md"
    md_path.write_text(f"# {title}\n\n{text}", encoding="utf-8")

    # --- .metadata.json ---
    metadata: dict = {
        "doc_id": pdf_path.stem,
        "title": title,
        "source_pdf": pdf_path.name,
        "markdown_file": md_path.name,
        "num_pages": num_pages,
        "topicos_detectados": topics,
        "parser": "PyMuPDF (fitz)" + (" + Tesseract OCR" if used_ocr else ""),
        "ocr_utilizado": used_ocr,
        "extraido_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "chunking": "src/rag/chunker.py",
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