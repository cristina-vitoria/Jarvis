"""JARVIS Acadêmico — ponto de entrada principal (CLI)."""

from src.agent import JarvisAgent
from src.rag.loader import carregar_documentos
from src.rag.chunker import chunk_documentos
from src.rag.vectorstore import construir_vectorstore
from src.config import DOCS_PATH


def inicializar_rag():
    """Carrega, chunka e indexa todos os documentos da pasta data/docs/."""
    documentos = carregar_documentos(DOCS_PATH)
    if not documentos:
        print("[JARVIS] Nenhum documento encontrado em data/docs/. O RAG estará desabilitado.")
        return None
    chunks = chunk_documentos(documentos)
    vectorstore = construir_vectorstore(chunks)
    print(f"[JARVIS] RAG inicializado com {len(chunks)} chunks de {len(documentos)} documentos.")
    return vectorstore


def main():
    print("=" * 50)
    print("  JARVIS Acadêmico — Assistente Inteligente")
    print("=" * 50)

    vectorstore = inicializar_rag()
    agente = JarvisAgent(vectorstore=vectorstore)

    print("\nDigite sua pergunta ou comando. Digite 'sair' para encerrar.")
    print("Durante um quiz, digite a letra da alternativa (A/B/C/D) ou 'cancelar'.\n")

    while True:
        try:
            # Indicador visual diferente quando quiz está ativo
            prefixo = "[Quiz] " if agente.quiz_session else "Você"
            user_input = input(f"{prefixo}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[JARVIS] Encerrando. Até logo!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit") and agente.quiz_session is None:
            print("[JARVIS] Encerrando. Até logo!")
            break

        resposta = agente.responder(user_input)
        print(f"\nJARVIS:\n{resposta}\n")


if __name__ == "__main__":
    main()