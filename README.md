# 🎓 JARVIS Acadêmico

Assistente pessoal inteligente para estudantes de graduação, com suporte a RAG, Tool Calling e LLM. Desenvolvido como trabalho prático da disciplina de Inteligência Artificial.

---

## 📌 Objetivo

O JARVIS Acadêmico auxilia estudantes a organizar e melhorar seu desempenho acadêmico, integrando:
- **RAG** — consulta a materiais de estudo (PDFs, textos, anotações)
- **Tool Calling** — chamada de ferramentas decidida pela LLM
- **LLM** — Qwen 2.5 14B como modelo principal
- **Melhorias de aprendizado** — geração de exercícios e quiz interativo com active recall

---

## 🏗️ Arquitetura

```
Usuário
  │
  ▼
[Interface CLI / Streamlit]
  │
  ▼
[Agent (Gemma 12B + Tool Calling)]
  │
  ├──► buscar_material_rag   → [RAG: FAISS + SentenceTransformers]
  ├──► consultar_agenda       → [agenda.json]
  ├──► listar_tarefas         → [tarefas.json]
  ├──► adicionar_tarefa       → [tarefas.json]
  ├──► concluir_tarefa        → [tarefas.json]
  ├──► gerar_exercicios       → [Qwen 2.5]
  └──► quiz_interativo        → [Qwen 2.5]
  │
  ▼
[Logger → logs/tool_calls.jsonl]
```

---

## 📁 Estrutura do Projeto

```
jarvis-academico/
├── README.md
├── requirements.txt
├── main.py
├── app_streamlit.py          ← Interface gráfica 
├── src/
│   ├── config.py
│   ├── llm_client.py         ← Integração Qwen 2.5 + seletor de ferramentas
│   ├── agent.py              ← Agente principal + QuizSession
│   ├── logger.py             ← Logs de tool calls (JSONL)
│   ├── rag/
│   │   ├── loader.py         ← Carregamento de PDFs e TXTs
│   │   ├── chunker.py        ← Divisão em chunks
│   │   ├── embeddings.py     ← Geração de embeddings
│   │   ├── vectorstore.py    ← Índice FAISS
│   │   └── retriever.py      ← Recuperação de trechos relevantes
│   ├── tools/
│   │   ├── agenda.py
│   │   ├── tarefas.py
│   │   ├── learning.py       ← gerar_exercicios e quiz_interativo
│   │   └── rag_tool.py
│   └── storage/
│       ├── agenda_store.py
│       └── tarefas_store.py
├── data/
│   ├── docs/                 ← PDFs das aulas (MC102 — UNICAMP)
│   │   └── README.md         ← Documentação do dataset
│   ├── agenda.json
│   └── tarefas.json
├── logs/
│   └── tool_calls.jsonl
├── evaluation/
│   ├── perguntas.json
│   ├── avaliar.py
│   ├── gerar_relatorio.py
│   ├── resultados.json
│   ├── relatorio.md          ← Relatório completo de avaliação
│   └── analise_erros.md      ← Análise de falhas identificadas
└── tests/
    ├── test_agenda.py
    ├── test_tarefas.py
    └── test_rag.py
```

---

## ⚙️ Como executar

### 1. Clonar o repositório
```bash
git clone https://github.com/cristina-vitoria/jarvis-academico.git
cd jarvis-academico
```

### 2. Criar e ativar o ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
Crie um arquivo `.env` na raiz e copie o '.env.example' colocando as informações necessárias.

### 5. Adicionar documentos acadêmicos
Os slides das aulas de MC102 já estão na pasta `data/docs/` (aula1.pdf a aula25.pdf).  
Para adicionar outros materiais, basta colocar arquivos `.pdf` ou `.txt` nessa pasta.

### 6. Rodar o sistema (CLI)
```bash
python main.py
```

### 7. Rodar a interface gráfica (Streamlit)
```bash
streamlit run app_streamlit.py
```

### 8. Executar os testes
```bash
pytest tests/
```

### 9. Executar a avaliação do sistema
```bash
python evaluation/avaliar.py
python evaluation/gerar_relatorio.py
```

---

## 🔧 Ferramentas (Tool Calling)

A decisão de chamada é feita pela própria LLM (Gemma 12B), que recebe a mensagem do usuário e um prompt estruturado com as ferramentas disponíveis, retornando JSON com `{"tool": "...", "args": {...}}`.

| Ferramenta | Descrição |
|---|---|
| `consultar_agenda` | Retorna compromissos por data ou período (`hoje`, `amanha`, `semana`) |
| `listar_tarefas` | Lista tarefas pendentes ou concluídas |
| `adicionar_tarefa` | Insere nova tarefa acadêmica |
| `concluir_tarefa` | Marca tarefa como concluída pelo ID numérico |
| `buscar_material_rag` | Recupera chunks relevantes e gera resposta com base nos documentos |
| `gerar_exercicios` | Gera exercícios de revisão sobre um tópico com o Gemma 12B |
| `quiz_interativo` | Inicia quiz de múltipla escolha com active recall e avaliação interativa |

Todos os logs de chamadas são registrados em `logs/tool_calls.jsonl` com ferramenta, entrada e saída.

---

## 📚 Dataset

- **Fonte:** Slides das aulas de MC102 — Algoritmos e Programação de Computadores  
  Professor Alexandre Xavier Falcão — IC/UNICAMP  
  Página oficial: https://www.ic.unicamp.br/~afalcao/mc102/
- **Localização:** `data/docs/` (aula1.pdf a aula25.pdf)
- **Quantidade:** 25 documentos
- **Formatos suportados:** PDF, TXT
- **Chunking:** 700 caracteres com overlap de 120 (configurável em `src/config.py`)
- **Impacto no RAG:** chunks menores aumentam precisão em detalhes pontuais; chunks maiores preservam contexto para respostas elaboradas
- **Limitações:** fórmulas matemáticas e tabelas em PDF podem ter extração imprecisa; tópicos avançados (complexidade, I/O detalhado) têm cobertura irregular entre as aulas

Ver documentação completa em [`data/docs/README.md`](data/docs/README.md).

---

## 📊 Avaliação do Sistema

O sistema foi avaliado com 23 perguntas. Resultados:

| Classificação | Quantidade | Percentual |
|---|---|---|
| Correta | 16 | 70% |
| Parcialmente correta | 3 | 13% |
| Incorreta | 4 | 17% |

Ver detalhes em [`evaluation/relatorio.md`](evaluation/relatorio.md).

---

## 🐛 Análise de Erros

Foram identificadas 4 categorias de falhas. Ver [`evaluation/analise_erros.md`](evaluation/analise_erros.md).

---

## 🤖 IAs utilizadas no desenvolvimento

- **Claude** — planejamento da arquitetura, revisão do código e sugestões de melhorias
- **Gemini** — revisão do código e sugestões de melhorias
- **Qwen 2.5** — modelo principal do sistema em produção

---

## 🛠️ Tecnologias

- Python 3.10+
- Qwen 2.5 (via API compatível com OpenAI)
- Sentence Transformers (`all-MiniLM-L6-v2`)
- FAISS
- pypdf
- Streamlit 
- pytest
