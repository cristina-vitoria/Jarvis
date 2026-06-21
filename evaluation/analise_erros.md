# Análise de Erros do JARVIS Acadêmico

Baseada nos resultados de `relatorio.md` (avaliação com 23 perguntas: **70% corretas, 13% parcialmente corretas, 17% incorretas**).  
Data de referência: 20/06/2026.

***

## Sumário das Falhas

| Categoria | Perguntas afetadas | Quantidade | Tipo |
|---|---|---|---|
| Retrieval gap — chunks pobres | 3, 10, 18 | 3 | Incorreta |
| Alucinação por conteúdo ausente | 23 | 1 | Incorreta |
| Contexto parcial (cobertura unilateral) | 11, 14, 16 | 3 | Parcialmente correta |
| Artefato de extração (caractere especial) | 9 | 1 | Correta com imprecisão |

***

## Falha 1 — Retrieval gap: chunks recuperados não contêm o tópico

**Tipo:** Falha de recuperação  
**Perguntas afetadas:** 3 (operadores lógicos AND/OR/NOT), 10 (complexidade de algoritmos de ordenação), 18 (formatos de I/O com exemplos)

### O que os logs mostram

- **Pergunta 3:** chunks recuperados foram `aula3.md (parte 3/7)`, `aula16.md (parte 1/9)` e `aula7.md (parte 1/7)` com scores baixos (`0.0`, `0.5195`, `0.6145`). Nenhum chunk menciona AND/OR/NOT. O agente respondeu corretamente que não encontrou o conteúdo — comportamento esperado — mas o problema é que o conteúdo existe no dataset (operadores lógicos são cobertos em MC102) e deveria ter sido recuperado.
- **Pergunta 10:** chunks recuperados foram `aula19.md (parte 3/7)`, `aula10.md (parte 3/8)` e `aula10.md (parte 1/8)`. Os dois chunks de `aula10` têm score `0.0`, indicando ausência de texto recuperável. O agente não encontrou complexidade de tempo nos materiais.
- **Pergunta 18:** chunks de `aula23` e `aula24` com scores `0.0` ou muito baixos. O agente não encontrou exemplos de I/O.

### Causa raiz

O problema **não é de extração de texto** — o PDF é lido corretamente. O problema é que slides com pseudocódigo, tabelas de complexidade e exemplos de código têm pouquíssimo texto corrido. Os chunks resultantes ficam com 30–60 tokens, sem contexto semântico suficiente para que o FAISS encontre correspondência com queries em linguagem natural. O BM25 também falha porque os termos da query (`"operadores lógicos"`) não coincidem lexicalmente com os símbolos nos chunks (`&&`, `||`, `!`).

### Solução recomendada

- **Contextual chunking:** prefixar cada chunk com o heading da seção pai no momento da indexação. Um chunk que contenha apenas `&&` e `||` se torna recuperável quando indexado como `"Operadores lógicos: && || !"`.
- **Aumentar `RAG_TOP_K` de 3 para 5–7** para ampliar o recall antes do Re-ranker filtrar.
- Inspecionar os chunks problemáticos com o script abaixo antes de qualquer outra ação:
  ```python
  from src.rag.chunker import carregar_chunks
  chunks = carregar_chunks()
  for c in chunks:
      if "operador" in c["texto"].lower() or "AND" in c["texto"]:
          print(c["fonte"], "---", c["texto"][:200])
  ```

***

## Falha 2 — Alucinação: uso de conhecimento paramétrico fora do contexto

**Tipo:** Falha de geração  
**Perguntas afetadas:** 23 (tipos de linguagens de programação)

### O que os logs mostram

- Chunks recuperados: `aula1.md (parte 6/13, score 0.6821)` e `aula1.md (parte 7/13, score 0.577)` — ambos com scores relevantes. O material da `aula1` de fato menciona linguagens de alto nível, baixo nível e de máquina.
- Diferente das perguntas 21 e 22 (Alan Turing / Máquina de Turing), onde o agente respondeu corretamente que não encontrou o conteúdo, na pergunta 23 o modelo **usou conhecimento paramétrico** para complementar a resposta além do que os chunks forneciam — gerando uma resposta tecnicamente correta mas não ancorada exclusivamente no material.

### Causa raiz

O prompt do agente contém `"NUNCA invente informações"` em nível global, mas não há instrução explícita **dentro da chamada de geração com contexto RAG** proibindo o uso de conhecimento externo. Quando os chunks recuperados são parcialmente relevantes (scores altos como 0.68), o modelo interpreta como sinal de que tem contexto suficiente e completa com conhecimento próprio sem sinalizar isso.

### Solução recomendada

Adicionar instrução restritiva diretamente no prompt de sistema da chamada RAG em `rag_tool.py`:

```python
messages = [
    {"role": "system", "content": (
        "Responda EXCLUSIVAMENTE com base no contexto abaixo. "
        "Se a resposta não estiver no contexto, diga: "
        "'Não encontrei essa informação nos materiais fornecidos.' "
        "É PROIBIDO usar conhecimento externo ao contexto, mesmo que você o conheça."
    )},
    {"role": "user", "content": f"Contexto:\n{contexto}\n\nPergunta: {pergunta}"}
]
```

***

## Falha 3 — Contexto parcial: cobertura unilateral do tópico recuperado

**Tipo:** Falha de geração (resposta incompleta)  
**Perguntas afetadas:** 11 (passagem de parâmetros), 14 (medidas de complexidade), 16 (vantagens de estruturas compostas)

### O que os logs mostram

- **Pergunta 11:** chunks de `aula16` recuperados cobrem somente passagem **por referência** (partes 5, 6 e 7 da aula16, scores 0.77 e 0.68). A resposta omite completamente passagem **por valor** — que é a outra metade da resposta esperada. O chunk com a explicação de passagem por valor provavelmente está em `aula16 (parte 4)` ou similar, mas não foi incluído nos top-3.
- **Pergunta 14:** chunks de `aula19` com scores `0.0` recuperam apenas O(n log n) e O(n²), omitindo O(n), O(1) e O(n³) que provavelmente aparecem em outras partes da aula. A resposta é classificada como parcial.
- **Pergunta 16:** somente listas dinâmicas foram recuperadas (`aula22, parte 1/7`). Vantagens de arrays e registros — que aparecem em `aula1` e `aula15` respectivamente — não foram incluídas nos top-3 chunks.

### Causa raiz

`RAG_TOP_K=3` é insuficiente para tópicos multifacetados onde a resposta completa está distribuída em mais de três chunks. O Re-ranker seleciona os melhores 3 de 15 candidatos, mas se os chunks relevantes para a segunda metade do tópico tiverem scores menores, eles são descartados antes de chegar ao LLM.

### Solução recomendada

- **Aumentar `RAG_TOP_K` para 5** no `.env` — impacto imediato e sem custo computacional relevante:
  ```env
  RAG_TOP_K=5
  RAG_RERANKER_CANDIDATES=20
  ```
- **Instrução de sinalização de cobertura parcial** no `SYSTEM_PROMPT`:
  ```
  - Se o contexto recuperado cobrir apenas parte do tópico, sinalize:
    "Encontrei informações parciais. O material disponível cobre: [subtópicos encontrados]."
  ```

## Observações Gerais

As perguntas 21 e 22 (Alan Turing / Máquina de Turing) demonstram que o sistema **funciona corretamente** quando o conteúdo não está no dataset: o agente responde que não encontrou a informação, sem alucinar. Esse é o comportamento esperado e deve ser preservado.

O padrão é claro: **o sistema performa bem em conteúdo textual contínuo e falha em conteúdo técnico-simbólico** (código, tabelas, símbolos matemáticos) onde os chunks têm baixa densidade semântica.
