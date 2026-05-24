# Análise de Erros do JARVIS Acadêmico

Baseada nos resultados de `relatorio.md` (avaliação com 23 perguntas: 70% corretas, 13% parcialmente corretas, 17% incorretas).

---

## Falha 1 — Ausência de conteúdo no dataset para tópicos específicos

**Tipo:** Falha de recuperação (retrieval gap)

**Perguntas afetadas:** Pergunta 3 (operadores lógicos AND/OR/NOT), Pergunta 10 (complexidade de algoritmos de ordenação), Pergunta 18 (formatos de I/O com exemplos)

**Causa:**  
O sistema respondeu corretamente que não encontrou informações nos materiais — o que é o comportamento esperado para evitar alucinação. Porém, o problema real é que esses tópicos **deveriam estar cobertos** pelo dataset (os slides de MC102 cobrem operadores lógicos, complexidade e I/O). A causa provável é que esses conteúdos estejam em slides com formatação que dificulta a extração via pypdf (código em caixas, pseudocódigo, tabelas), resultando em chunks com texto insuficiente ou vazio para esses tópicos.

**Possível solução:**
- Complementar o dataset com versões `.txt` dos tópicos problemáticos, escritas manualmente.
- Inspecionar os chunks gerados para esses tópicos e validar se o conteúdo foi extraído corretamente.

---

## Falha 2 — Resposta parcial por cobertura unilateral do contexto recuperado

**Tipo:** Falha de geração (resposta incompleta / contexto parcial)

**Perguntas afetadas:** Pergunta 11 (passagem de parâmetros por valor e por referência), Pergunta 14 (medidas de complexidade), Pergunta 16 (vantagens de estruturas compostas)

**Causa:**  
O retriever recuperou chunks que cobriam apenas **uma parte** do tópico (ex.: somente passagem por referência, somente O(n log n) e O(n²), somente listas dinâmicas), e a LLM gerou a resposta limitada ao contexto recebido, sem sinalizar que o assunto era mais amplo. O problema combina cobertura incompleta dos chunks recuperados com ausência de mecanismo que indique ao modelo que o contexto pode ser parcial.

**Possível solução:**
- Aumentar o número de chunks recuperados (top-k) de 3 para 5–7, para ampliar a cobertura do contexto enviado à LLM.
- Adicionar ao prompt RAG uma instrução explícita pedindo ao modelo que sinalize quando perceber que o contexto cobre apenas parte do tópico.
- Implementar recuperação por múltiplas queries (query expansion) para tópicos com múltiplos subtópicos.

---

## Falha 3 — Alucinação em perguntas fora do escopo do dataset

**Tipo:** Falha de geração (alucinação)

**Perguntas afetadas:** Pergunta 23 (tipos de linguagens de programação e características)

**Causa:**  
A pergunta sobre tipos de linguagens de programação (alto nível, baixo nível, máquina) tem relação com o conteúdo de MC102, mas o sistema **não encontrou o trecho relevante** nos chunks. Em vez de responder que não localizou a informação (como fez corretamente nas perguntas 21 e 22 sobre Alan Turing), o modelo usou conhecimento paramétrico e **gerou uma resposta sem base nos documentos**. Isso indica que o prompt da ferramenta RAG não é suficientemente restritivo quanto ao uso de conhecimento externo ao contexto recuperado."
**Possível solução:**
- Adicionar ao prompt principal da ferramenta RAG uma instrução explícita: "Se o contexto não contiver informação suficiente, responda que não encontrou nos materiais. Nunca use conhecimento externo ao contexto."
- Monitorar os logs (`tool_calls.jsonl`) para identificar padrões em que a resposta não tem ancoragem no contexto.

---

## Falha 4 — Imprecisão na representação de caracteres especiais na geração

**Tipo:** Falha de geração (artefato de extração / codificação)

**Perguntas afetadas:** Pergunta 9 (cadeias de caracteres — o terminador `\0` apareceu como `?` na resposta)

**Causa:**  
O caractere `\0` (null terminator de strings em C), ao ser extraído do PDF e armazenado no chunk, perde sua representação original e aparece como `?` ou outro símbolo de substituição. A LLM então reproduz esse artefato na resposta, gerando uma explicação tecnicamente imprecisa para o estudante.

**Possível solução:**
- Adicionar ao dataset versões `.txt` das aulas mais técnicas, garantindo que os caracteres especiais estejam corretamente representados.