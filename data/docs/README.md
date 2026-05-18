# Dataset — JARVIS Acadêmico

Esta pasta contém os documentos acadêmicos usados como base de conhecimento para o RAG. Cada material foi selecionado para oferecer cobertura conceitual suficiente para perguntas, resumos e respostas fundamentadas nos trechos recuperados.

---

## Documentos incluídos

| # | Código | Documento | Tipo | Disciplina | Origem | Limitações |
|---|---|---|---|---|---|---|
| 7 | `ch2-8_*` | MIT 6.034: Artificial Intelligence — Lecture Notes (2005) | Notas de aula universitária | Inteligência Artificial | MIT OpenCourseWare / Patrick H. Winston | Material antigo; não cobre LLMs, transformers ou RAG; OCR pode degradar fórmulas |
| 1 | `DEEP LEARNING ( R20A06610 )` | Deep Learning Notes — MRCET | Apostila universitária (PDF) | Inteligência Artificial | MRCET — Departamento de CSE | Não cobre bem transformers modernos; extração de fórmulas e diagramas pode falhar |
| 1 | `AI_Unit_1` | Artificial Intelligence — Unit 1 Notes | Notas de aula (PDF) | Inteligência Artificial | JECRC Foundation | Cobre apenas a Unit 1; possui redundância em conteúdos de busca e introdução |
| 1 | `COS324_Course_Notes` | A Princeton COS 324: Introduction to Machine Learning | Livro-texto de curso aberto (PDF) | Inteligência Artificial | Princeton University | Nível introdutório. Matemática acessível mas não aprofundada. Sem LLMs/RAG |

---

## Organização do dataset

Os documentos foram organizados por **disciplina** e identificados individualmente por código (`DOC-XX`) para facilitar indexação, rastreabilidade no RAG e análise posterior de recuperação. Essa estrutura também ajuda a separar materiais introdutórios, apostilas extensas e notas por unidade curricular.

## Estratégia de Chunking

- **Método:** chunking por tamanho fixo com overlap
- **Chunk size:** 700 caracteres
- **Overlap:** 120 caracteres
- **Configurável em:** `src/config.py` via variáveis `CHUNK_SIZE` e `CHUNK_OVERLAP`

### Impacto no RAG

---

## Origem e limitações

Os documentos deste dataset foram obtidos de fontes acadêmicas abertas ou distribuídos para uso educacional. O conjunto tem boa cobertura para fundamentos de Inteligência Artificial e Deep Learning clássico, mas possui limitações em tópicos recentes como LLMs, transformers e sistemas RAG modernos.

Além disso, alguns PDFs apresentam diagramação acadêmica densa, figuras e fórmulas com OCR imperfeito, o que pode afetar a qualidade da indexação textual e da recuperação semântica.

---

## Como adicionar documentos

1. Coloque o arquivo (PDF ou TXT) nesta pasta.
2. Atualize este README com origem, tipo, cobertura e limitações.
3. Reinicie o sistema (`python main.py` ou reinicie o app Streamlit).
4. O RAG será reindexado automaticamente.