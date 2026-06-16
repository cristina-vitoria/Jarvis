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
[Agent (Qwen 2.5 + Tool Calling)]
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
├── .env.example              ← Modelo de configuração (copie para .env)
├── main.py
├── app_streamlit.py          ← Interface gráfica
├── src/
│   ├── config.py
│   ├── llm_client.py         ← Integração Qwen 2.5 + seletor de ferramentas
│   ├── agent.py              ← Agente principal + QuizSession
│   ├── logger.py             ← Logs de tool calls (JSONL)
│   ├── rag/
│   │   ├── loader.py         ← Carregamento de PDFs e TXTs
│   │   ├── pdf_converter.py  ← Conversão de PDF para Markdown estruturado
│   │   ├── chunker.py        ← Divisão semântica em chunks por headings
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

## ⚙️ Pré-requisitos do sistema

Antes de instalar as dependências Python, certifique-se de ter:

### Python 3.11
> ⚠️ **Python 3.12+ pode funcionar, mas Python 3.13 não é suportado** pelo PyTorch e causará erro `[WinError 1114]` no Windows.

- Download: https://www.python.org/downloads/release/python-3119/
- Durante a instalação, marque ✅ **"Add python.exe to PATH"**

### Git
- Download: https://git-scm.com/downloads

### Tesseract OCR *(opcional — apenas para PDFs escaneados)*

Necessário somente se os PDFs não tiverem camada de texto nativa (imagens de scans).

| Sistema | Comando / Link |
|---|---|
| **Windows** | [Instalador UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) — marque "Additional language data (Portuguese)" |
| **Ubuntu/Debian** | `sudo apt install tesseract-ocr tesseract-ocr-por` |
| **macOS** | `brew install tesseract` |

Após instalar no Windows, adicione o caminho ao PATH do sistema (ex: `C:\Program Files\Tesseract-OCR`).

---

## ⚙️ Como executar

### 1. Clonar o repositório
```bash
git clone https://github.com/cristina-vitoria/Jarvis.git
cd Jarvis
```

### 2. Criar e ativar o ambiente virtual com Python 3.11

**Linux / macOS:**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

> Se o comando `py -3.11` não funcionar, use o caminho completo:
> `C:\Users\SeuUsuario\AppData\Local\Programs\Python\Python311\python.exe -m venv venv`

### 3. Instalar PyTorch (CPU-only)

> ⚠️ **Este passo deve ser feito ANTES de instalar o `requirements.txt`.**  
> O `pip install torch` padrão baixa a versão com CUDA, que falha em máquinas sem GPU NVIDIA.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Verifique a instalação:
```bash
python -c "import torch; print('PyTorch OK:', torch.__version__)"
```

### 4. Instalar demais dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha com as informações fornecidas pelo professor:

```bash
cp .env.example .env   # Linux/macOS
copy .env.example .env  # Windows
```

Edite o `.env` com as credenciais da API:
```env
LLM_BASE_URL=https://url-fornecida-pelo-professor/v1
LLM_API_KEY=seu-token-aqui
```

### 6. Adicionar documentos acadêmicos

Os slides de MC102 (UNICAMP) já estão em `data/docs/` (aula1.pdf a aula25.pdf).  
Para adicionar outros materiais, coloque arquivos `.pdf` ou `.txt` nessa pasta.

### 7. Rodar o sistema

**Interface de linha de comando:**
```bash
python main.py
```

**Interface gráfica (Streamlit):**
```bash
streamlit run app_streamlit.py
```

Acesse em: http://localhost:8501

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

A decisão de chamada é feita pela própria LLM, que recebe a mensagem do usuário e um prompt estruturado com as ferramentas disponíveis, retornando JSON com `{"tool": "...", "args": {...}}`.

| Ferramenta | Descrição |
|---|---|
| `consultar_agenda` | Retorna compromissos por data ou período (`hoje`, `amanha`, `semana`) |
| `listar_tarefas` | Lista tarefas pendentes ou concluídas |
| `adicionar_tarefa` | Insere nova tarefa acadêmica |
| `concluir_tarefa` | Marca tarefa como concluída pelo ID numérico |
| `buscar_material_rag` | Recupera chunks relevantes e gera resposta com base nos documentos |
| `gerar_exercicios` | Gera exercícios de revisão sobre um tópico com o Qwen 2.5 |
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
- **Chunking:** semântico por headings (tamanho máximo 1000 chars, overlap 150) — configurável via `.env`
- **Impacto no RAG:** o chunking por headings preserva a coerência semântica de cada slide; o limite de 1000 chars evita cortar seções densas ao meio
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

| Tecnologia | Versão mínima | Uso |
|---|---|---|
| Python | **3.11** | Runtime (3.13 não suportado) |
| PyTorch | 2.2.0 (CPU) | Backend do sentence-transformers |
| Qwen 2.5 14B | — | LLM principal (via API do professor) |
| Sentence Transformers | 2.7.0 | Geração de embeddings |
| FAISS-CPU | 1.8.0 | Índice vetorial |
| PyMuPDF | 1.24.0 | Extração de PDF com estrutura |
| Streamlit | 1.35.0 | Interface gráfica |
| pytest | 8.2.0 | Testes automatizados |
| Tesseract OCR | 5.x *(opcional)* | OCR para PDFs escaneados |
