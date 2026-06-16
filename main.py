"""JARVIS Acadêmico — ponto de entrada principal (CLI).

Uso:
    python main.py

Durante um quiz, o prompt muda para '[Quiz] Resposta:' e aceita:
  - Letra da alternativa: A, B, C ou D
  - 'cancelar' para encerrar o quiz
"""

from src.agent import JarvisAgent
from src.rag.loader import carregar_documentos
from src.rag.chunker import chunk_documentos
from src.rag.vectorstore import construir_vectorstore
from src.config import DOCSMD_PATH
from src.config import RAG_HYBRID_ENABLED
from src.rag.bm25_store import BM25Store


def inicializar_rag():
    """Carrega, chunka e indexa todos os .md de data/docsmd/."""
    documentos = carregar_documentos(DOCSMD_PATH)
    if not documentos:
        print(
            "[JARVIS] Nenhum documento encontrado em data/docsmd/.\n"
            "[JARVIS] Execute: python data/scripts/extract_pdf.py\n"
            "[JARVIS] O RAG estará desabilitado até lá."
        )
        return None
    chunks = chunk_documentos(documentos)
    vectorstore = construir_vectorstore(chunks)
    bm25 = BM25Store(chunks) if RAG_HYBRID_ENABLED else None
    print(f"[JARVIS] RAG inicializado com {len(chunks)} chunks de {len(documentos)} documentos.")
    return vectorstore, bm25


def main():
    print("=" * 55)
    print("  JARVIS Acadêmico — Assistente Inteligente")
    print("=" * 55)
    print("Comandos: 'sair' para encerrar | 'cancelar' durante quiz")
    print("-" * 55)

    vectorstore, bm25 = inicializar_rag()
    agente = JarvisAgent(vectorstore=vectorstore, bm25_store=bm25)

    print("\nSistema pronto. Digite sua mensagem abaixo.\n")

    while True:
        try:
            if agente.quiz_session is not None:
                sess = agente.quiz_session
                idx = sess.indice_atual + 1
                total = len(sess.perguntas)
                prefixo = f"[Quiz {idx}/{total}] Resposta"
            else:
                prefixo = "Você"

            user_input = input(f"\n{prefixo}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[JARVIS] Encerrando. Até logo!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("sair", "exit", "quit") and agente.quiz_session is None:
            print("[JARVIS] Encerrando. Até logo!")
            break

        resposta = agente.responder(user_input)
        print(f"\nJARVIS:\n{resposta}")

        if agente.quiz_session is None and "Quiz finalizado" in resposta:
            print("\n" + "-" * 55)
            print("Quiz encerrado. Continue estudando! 📚")
            print("-" * 55)


if __name__ == "__main__":
    main()