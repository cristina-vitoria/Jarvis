"""Carregamento de documentos da pasta data/docs/."""

from pathlib import Path


def _ler_pdf(caminho: Path) -> str:
    """Extrai texto de um arquivo PDF."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(caminho))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"[Loader] Erro ao ler PDF '{caminho.name}': {e}")
        return ""


def _ler_txt(caminho: Path) -> str:
    """Extrai texto de um arquivo .txt."""
    try:
        return caminho.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[Loader] Erro ao ler TXT '{caminho.name}': {e}")
        return ""


def carregar_documentos(docs_path: Path) -> list[dict]:
    """
    Carrega todos os documentos da pasta.

    Returns:
        Lista de dicts com {'nome': str, 'texto': str}.
    """
    documentos = []
    extensoes = {".pdf": _ler_pdf, ".txt": _ler_txt}

    for arquivo in sorted(docs_path.iterdir()):
        if arquivo.suffix.lower() in extensoes:
            texto = extensoes[arquivo.suffix.lower()](arquivo)
            if texto.strip():
                documentos.append({"nome": arquivo.name, "texto": texto})
                print(f"[Loader] Carregado: {arquivo.name} ({len(texto)} caracteres)")

    return documentos