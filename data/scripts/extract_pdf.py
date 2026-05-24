"""Script CLI para converter PDFs em batch.

Uso:
    python data/scripts/extract_pdf.py
    python data/scripts/extract_pdf.py --docs data/docs --out data/docsmd

Responsabilidade ÚNICA: chamar converter_pdf() para cada PDF encontrado.
Toda lógica de extração/limpeza fica em src/rag/pdf_converter.py.
"""
from __future__ import annotations

import argparse
from pathlib import Path

# garante que src/ seja encontrável ao rodar direto
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.rag.pdf_converter import converter_pdf


def main() -> None:
    parser = argparse.ArgumentParser(description="Converte PDFs em .md + .metadata.json")
    parser.add_argument("--docs", default="data/docs", help="Pasta com os PDFs originais")
    parser.add_argument("--out",  default="data/docsmd", help="Pasta de saída dos .md")
    args = parser.parse_args()

    docs_dir = Path(args.docs)
    out_dir  = Path(args.out)

    pdfs = sorted(docs_dir.glob("*.pdf"))
    if not pdfs:
        print(f"[extract_pdf] Nenhum PDF encontrado em '{docs_dir}'.")
        return

    for pdf_path in pdfs:
        try:
            md_path, meta_path = converter_pdf(pdf_path, out_dir)
            print(f"[extract_pdf] ✓ {pdf_path.name} → {md_path.name} + {meta_path.name}")
        except ValueError as e:
            print(f"[extract_pdf] ✗ {pdf_path.name}: {e}")
        except Exception as e:
            print(f"[extract_pdf] ✗ {pdf_path.name}: erro inesperado — {e}")


if __name__ == "__main__":
    main()