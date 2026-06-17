"""Construção e persistência do índice FAISS."""

import faiss
from src.rag.embeddings import gerar_embeddings, gerar_embedding_query


class VectorStore:
    """Armazena chunks e o índice FAISS para busca semântica."""

    def __init__(self, chunks: list[dict]):
        if not chunks:
            raise ValueError(
                "Não é possível criar um VectorStore vazio. "
                "Carregue ao menos um documento antes de indexar."
            )
        self.chunks = chunks
        textos = [c["texto"] for c in chunks]
        embeddings = gerar_embeddings(textos)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner Product = cosseno com vetores normalizados
        self.index.add(embeddings)
        print(f"[VectorStore] Índice FAISS criado com {self.index.ntotal} vetores (dim={dim}).")

    def buscar(self, query: str, k: int = 3) -> list[dict]:
        """Retorna os k chunks mais relevantes para a query."""
        q_emb = gerar_embedding_query(query)
        distancias, indices = self.index.search(q_emb, k)
        resultados = []
        for score, idx in zip(distancias[0], indices[0]):
            if idx >= 0:
                chunk = dict(self.chunks[idx])
                chunk["score"] = float(score)
                resultados.append(chunk)
        return resultados

    def listar_fontes(self) -> list[dict]:
        """
        Retorna uma entrada por documento único indexado.

        Cada entrada contém:
            'fonte'       : nome do arquivo .md
            'doc_id'      : identificador do documento (quando disponível)
            'title'       : título legível               (quando disponível)
            'topicos'     : lista de tópicos detectados  (quando disponível)
            'num_chunks'  : quantidade de chunks deste documento
            'headings'    : lista de headings únicos indexados (chunking semântico)
            'estrategia'  : 'heading' | 'fixo' | 'misto' conforme os chunks do doc
        """
        vistos: dict[str, dict] = {}  # fonte -> info
        for chunk in self.chunks:
            fonte = chunk["fonte"]
            if fonte not in vistos:
                vistos[fonte] = {
                    "fonte": fonte,
                    "doc_id": chunk.get("doc_id", fonte.rsplit(".", 1)[0]),
                    "title": chunk.get("title", fonte),
                    "topicos": chunk.get("topicos_detectados", []),
                    "num_chunks": 0,
                    "headings": [],
                    "_estrategias": set(),
                }
            vistos[fonte]["num_chunks"] += 1

            # Coleta headings únicos (preserva ordem de aparição)
            heading = chunk.get("heading_secao", "").strip()
            # Remove sufixo de sub-chunk "(parte N/M)" para deduplicação
            heading_base = heading.split(" (parte ")[0].strip() if heading else ""
            if heading_base and heading_base not in vistos[fonte]["headings"]:
                vistos[fonte]["headings"].append(heading_base)

            estrategia = chunk.get("estrategia_chunking", "")
            if estrategia:
                vistos[fonte]["_estrategias"].add(estrategia)

        # Pós-processa campos derivados
        resultado = []
        for info in vistos.values():
            estrategias = info.pop("_estrategias")
            if len(estrategias) > 1:
                info["estrategia"] = "misto"
            else:
                info["estrategia"] = next(iter(estrategias), "desconhecido")
            resultado.append(info)

        return resultado


def construir_vectorstore(chunks: list[dict]) -> VectorStore:
    """Factory para criar e retornar um VectorStore."""
    return VectorStore(chunks)
