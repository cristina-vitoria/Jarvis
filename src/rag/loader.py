"""Carregamento de documentos para o pipeline RAG.

Fonte única: data/docsmd/
    Somente arquivos .md são lidos.
    O sidecar .metadata.json gerado pelo pdf_converter é lido quando presente
    e seus campos são mesclados no dicionário do documento.

Fluxo completo:
    1. Usuário coloca PDFs em data/docs/
    2. python data/scripts/extract_pdf.py  ->  gera .md + .metadata.json em data/docsmd/
    3. Este loader lê data/docsmd/*.md  (+  *.metadata.json quando presentes)
    4. src/rag/chunker.py divide o texto em chunks
    5. src/rag/embeddings.py + vectorstore.py indexam os chunks
"""

import json
from pathlib import Path

from src.config import DOCSMD_PATH


def _ler_md(caminho: Path) -> str:
    """Lê um arquivo Markdown como texto simples."""
    try:
        return caminho.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[Loader] Erro ao ler '{caminho.name}': {e}")
        return ""


def _ler_metadata(md_path: Path) -> dict:
    """
    Tenta ler o sidecar <stem>.metadata.json ao lado do .md.

    Retorna dict vazio se o arquivo não existir ou for inválido.
    Campos esperados (gerados pelo pdf_converter):
        doc_id, title, source_pdf, markdown_file, num_pages,
        topicos_detectados, parser, ocr_utilizado, extraido_em, chunking,
        disciplina (opcional), fonte (opcional), fonte_url (opcional), licenca (opcional)
    """
    meta_path = md_path.with_suffix(".metadata.json")
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[Loader] Aviso: não foi possível ler '{meta_path.name}': {e}")
        return {}


def carregar_documentos(docs_path: Path = DOCSMD_PATH) -> list[dict]:
    """
    Carrega todos os arquivos .md de docs_path (padrão: data/docsmd/).

    Cada documento retornado contém:
        'nome'   : nome do arquivo .md  (ex: aula1.md)
        'texto'  : conteúdo completo do .md
        + todos os campos do .metadata.json quando presente
          (doc_id, title, topicos_detectados, ocr_utilizado, etc.)

    Returns:
        Lista de dicts.
    """
    md_files = sorted(docs_path.glob("*.md"))

    if not md_files:
        print(
            f"[Loader] Nenhum arquivo .md encontrado em '{docs_path}'.\n"
            "[Loader] Execute primeiro: python data/scripts/extract_pdf.py"
        )
        return []

    documentos = []
    for arquivo in md_files:
        texto = _ler_md(arquivo)
        if not texto.strip():
            print(f"[Loader] Ignorado (sem texto): {arquivo.name}")
            continue

        doc: dict = {"nome": arquivo.name, "texto": texto}

        # Mescla metadados do sidecar (quando presente)
        meta = _ler_metadata(arquivo)
        if meta:
            # 'nome' e 'texto' têm prioridade — não deixa o sidecar sobrescrever
            for k, v in meta.items():
                if k not in ("nome", "texto"):
                    doc[k] = v
            doc_id = meta.get("doc_id", arquivo.stem)
            print(f"[Loader] Carregado: {arquivo.name} | doc_id={doc_id} | "
                  f"{len(texto)} chars | ocr={meta.get('ocr_utilizado', '?')}")
        else:
            print(f"[Loader] Carregado: {arquivo.name} ({len(texto)} caracteres) [sem metadata]")

        documentos.append(doc)

    print(f"[Loader] Total de documentos carregados: {len(documentos)}")
    return documentos