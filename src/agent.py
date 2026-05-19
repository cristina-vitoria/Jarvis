"""Orquestrador principal do JARVIS Acadêmico."""

import traceback
from src.llm_client import gerar_resposta, decidir_ferramenta
from src.logger import log_tool_call
from src.config import SYSTEM_PROMPT
from src.tools.agenda import consultar_agenda
from src.tools.tarefas import listar_tarefas, adicionar_tarefa, concluir_tarefa
from src.tools.learning import gerar_exercicios, iniciar_quiz, avaliar_resposta_quiz
from src.tools.rag_tool import buscar_material_rag

# Schema das ferramentas disponíveis para o modelo
TOOLS_SCHEMA = [
    {
        "name": "consultar_agenda",
        "description": "Consulta compromissos acadêmicos por data específica ou período (hoje, amanha, semana).",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Data no formato YYYY-MM-DD (opcional)"},
                "periodo": {"type": "string", "description": "hoje | amanha | semana (opcional)"},
            },
        },
    },
    {
        "name": "listar_tarefas",
        "description": "Lista as tarefas acadêmicas. Pode filtrar por status: pendente ou concluida.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "pendente | concluida (opcional)"},
            },
        },
    },
    {
        "name": "adicionar_tarefa",
        "description": "Adiciona uma nova tarefa acadêmica.",
        "parameters": {
            "type": "object",
            "properties": {
                "titulo": {"type": "string", "description": "Título da tarefa (obrigatório)"},
                "prazo": {"type": "string", "description": "Prazo no formato YYYY-MM-DD (opcional)"},
                "disciplina": {"type": "string", "description": "Nome da disciplina (opcional)"},
            },
            "required": ["titulo"],
        },
    },
    {
        "name": "concluir_tarefa",
        "description": "Marca uma tarefa como concluída pelo ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "id_tarefa": {"type": "integer", "description": "ID numérico da tarefa"},
            },
            "required": ["id_tarefa"],
        },
    },
    {
        "name": "buscar_material_rag",
        "description": "Busca informações nos materiais de estudo (PDFs e textos). Use para perguntas acadêmicas.",
        "parameters": {
            "type": "object",
            "properties": {
                "pergunta": {"type": "string", "description": "Pergunta ou tópico a ser buscado"},
            },
            "required": ["pergunta"],
        },
    },
    {
        "name": "gerar_exercicios",
        "description": "Gera exercícios de revisão sobre um tópico acadêmico.",
        "parameters": {
            "type": "object",
            "properties": {
                "topico": {"type": "string", "description": "Tópico para geração dos exercícios"},
                "quantidade": {"type": "integer", "description": "Número de exercícios (padrão: 3)"},
            },
            "required": ["topico"],
        },
    },
    {
        "name": "quiz_interativo",
        "description": "Inicia um quiz interativo de active recall sobre um tópico. O sistema faz uma pergunta e avalia a resposta.",
        "parameters": {
            "type": "object",
            "properties": {
                "topico": {"type": "string", "description": "Tópico para o quiz"},
                "num_perguntas": {"type": "integer", "description": "Quantidade de perguntas no quiz (padrão: 3)"},
            },
            "required": ["topico"],
        },
    },
]


class QuizSession:
    """Mantém o estado de uma sessão de quiz em andamento."""

    def __init__(self, topico: str, perguntas: list[dict]):
        """
        perguntas: lista de dicts com chaves:
          - enunciado: str
          - opcoes: list[str]  (para multiple-choice, ex: ['A) ...', 'B) ...', ...])
          - gabarito: str  (letra correta, ex: 'A')
          - explicacao: str
        """
        self.topico = topico
        self.perguntas = perguntas
        self.indice_atual = 0
        self.acertos = 0
        self.historico_respostas: list[dict] = []  # {pergunta, resposta_aluno, correto, feedback}

    @property
    def concluido(self) -> bool:
        return self.indice_atual >= len(self.perguntas)

    @property
    def pergunta_atual(self) -> dict | None:
        if self.concluido:
            return None
        return self.perguntas[self.indice_atual]

    def registrar_resposta(self, resposta_aluno: str, correto: bool, feedback: str):
        self.historico_respostas.append({
            "pergunta": self.pergunta_atual["enunciado"],
            "opcoes": self.pergunta_atual.get("opcoes", []),
            "gabarito": self.pergunta_atual.get("gabarito", ""),
            "resposta_aluno": resposta_aluno,
            "correto": correto,
            "feedback": feedback,
        })
        if correto:
            self.acertos += 1
        self.indice_atual += 1

    def relatorio_final(self) -> str:
        total = len(self.perguntas)
        pct = int(self.acertos / total * 100) if total else 0
        linhas = [
            f"## 🏁 Quiz finalizado — {self.topico}",
            f"**Resultado: {self.acertos}/{total} ({pct}%)**",
            "",
        ]
        emoji_nota = "🏆" if pct >= 80 else ("👍" if pct >= 50 else "📖")
        linhas.append(f"{emoji_nota} {'Excelente!' if pct >= 80 else ('Bom trabalho!' if pct >= 50 else 'Continue estudando!')}")
        linhas.append("")
        for i, r in enumerate(self.historico_respostas, 1):
            status = "✅" if r["correto"] else "❌"
            linhas.append(f"**{i}. {r['pergunta']}**")
            if r.get("opcoes"):
                for op in r["opcoes"]:
                    linhas.append(f"   {op}")
            linhas.append(f"   Sua resposta: **{r['resposta_aluno']}** {status}")
            if not r["correto"]:
                linhas.append(f"   Gabarito: **{r['gabarito']}**")
            linhas.append(f"   💡 {r['feedback']}")
            linhas.append("")
        return "\n".join(linhas)


class JarvisAgent:
    def __init__(self, vectorstore=None):
        self.vectorstore = vectorstore
        self.historico = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Estado do quiz em andamento (None quando não há quiz ativo)
        self.quiz_session: QuizSession | None = None

    # ------------------------------------------------------------------
    # Quiz helpers
    # ------------------------------------------------------------------

    def _formatar_pergunta_quiz(self) -> str:
        """Formata a pergunta atual do quiz para exibição."""
        sess = self.quiz_session
        q = sess.pergunta_atual
        total = len(sess.perguntas)
        idx = sess.indice_atual + 1
        linhas = [
            f"🧠 **Quiz: {sess.topico}** — Pergunta {idx}/{total}",
            "",
            f"**{q['enunciado']}**",
        ]
        if q.get("opcoes"):
            linhas.append("")
            for op in q["opcoes"]:
                linhas.append(op)
            linhas.append("")
            linhas.append("Digite a letra da alternativa correta (A, B, C ou D):")
        else:
            linhas.append("")
            linhas.append("Digite sua resposta:")
        return "\n".join(linhas)

    def _processar_resposta_quiz(self, resposta_aluno: str) -> str:
        """Avalia a resposta do aluno na pergunta atual e avança o quiz."""
        sess = self.quiz_session
        q = sess.pergunta_atual
        gabarito = q.get("gabarito", "").strip().upper()
        resposta_normalizada = resposta_aluno.strip().upper().lstrip(".").strip()

        # Para multiple-choice compara apenas a letra
        if q.get("opcoes"):
            correto = resposta_normalizada.startswith(gabarito)
        else:
            # Resposta aberta: pede feedback ao LLM
            prompt_aval = (
                f"Pergunta: {q['enunciado']}\n"
                f"Resposta esperada: {q.get('explicacao', gabarito)}\n"
                f"Resposta do aluno: {resposta_aluno}\n\n"
                "A resposta do aluno está correta, mesmo que com palavras diferentes? "
                "Responda apenas SIM ou NAO."
            )
            veredicto = gerar_resposta([{"role": "user", "content": prompt_aval}])
        correto = "SIM" in veredicto.upper() if not q.get("opcoes") else correto

        feedback = q.get("explicacao", "")
        sess.registrar_resposta(resposta_aluno, correto, feedback)

        if sess.concluido:
            relatorio = sess.relatorio_final()
            self.quiz_session = None
            return relatorio

        status_msg = "✅ Correto!" if correto else f"❌ Incorreto. A resposta certa era **{gabarito}**."
        return (
            status_msg
            + (f"\n💡 {feedback}" if feedback else "")
            + "\n\n"
            + self._formatar_pergunta_quiz()
        )

    # ------------------------------------------------------------------
    # Execução de ferramentas
    # ------------------------------------------------------------------

    def _executar_ferramenta(self, tool_name: str, arguments: dict) -> str:
        """
        Executa a ferramenta correspondente e retorna o resultado como string.
        Envolve toda execução em try/except para isolar falhas e registrar no log.
        """
        resultado = None
        try:
            if tool_name == "consultar_agenda":
                resultado = consultar_agenda(**arguments)

            elif tool_name == "listar_tarefas":
                resultado = listar_tarefas(**arguments)

            elif tool_name == "adicionar_tarefa":
                resultado = adicionar_tarefa(**arguments)

            elif tool_name == "concluir_tarefa":
                resultado = concluir_tarefa(**arguments)

            elif tool_name == "buscar_material_rag":
                if self.vectorstore is None:
                    resultado = "RAG não disponível: nenhum documento foi carregado."
                else:
                    resultado = buscar_material_rag(
                        pergunta=arguments.get("pergunta", ""),
                        vectorstore=self.vectorstore,
                        llm_fn=lambda msg: gerar_resposta(msg),
                    )

            elif tool_name == "gerar_exercicios":
                if self.vectorstore is None:
                    resultado = "Exercícios não disponíveis: nenhum documento foi carregado."
                else:
                    resultado = gerar_exercicios(
                        topico=arguments.get("topico", ""),
                        vectorstore=self.vectorstore,
                        llm_fn=lambda msg: gerar_resposta(msg),
                        quantidade=arguments.get("quantidade", 3),
                    )

            elif tool_name == "quiz_interativo":
                if self.vectorstore is None:
                    resultado = "Quiz não disponível: nenhum documento foi carregado."
                else:
                    resultado = self._iniciar_quiz(
                        topico=arguments.get("topico", ""),
                        num_perguntas=arguments.get("num_perguntas", 3),
                    )

            else:
                resultado = f"Ferramenta '{tool_name}' não reconhecida."

        except TypeError as exc:
            resultado = (
                f"[ERRO] Argumentos inválidos para '{tool_name}': {exc}. "
                "Verifique os parâmetros e tente novamente."
            )
            print(f"[JARVIS][TypeError] {tool_name}: {exc}")

        except FileNotFoundError as exc:
            resultado = (
                f"[ERRO] Arquivo de dados não encontrado ao executar '{tool_name}': {exc}."
            )
            print(f"[JARVIS][FileNotFoundError] {tool_name}: {exc}")

        except Exception as exc:  # noqa: BLE001
            resultado = (
                f"[ERRO] Falha inesperada ao executar a ferramenta '{tool_name}'. "
                "Por favor, tente novamente ou reformule sua solicitação."
            )
            print(f"[JARVIS][Exception] {tool_name}: {exc}")
            print(traceback.format_exc())

        log_tool_call(tool_name, arguments, resultado)
        return str(resultado)

    def _iniciar_quiz(self, topico: str, num_perguntas: int = 3) -> str:
        """
        Gera as perguntas do quiz via LLM e armazena em self.quiz_session.
        Retorna a primeira pergunta formatada.
        """
        prompt = (
            f"Crie exatamente {num_perguntas} perguntas de múltipla escolha sobre o tópico: '{topico}'.\n"
            "Para cada pergunta, use EXATAMENTE este formato (sem variações):\n"
            "PERGUNTA: <enunciado>\n"
            "A) <opção A>\n"
            "B) <opção B>\n"
            "C) <opção C>\n"
            "D) <opção D>\n"
            "GABARITO: <letra>\n"
            "EXPLICACAO: <explicação curta de por que a resposta está correta>\n"
            "---\n"
            "Gere apenas as perguntas no formato acima, sem texto extra antes ou depois."
        )
        raw = gerar_resposta([{"role": "user", "content": prompt}])
        perguntas = _parsear_quiz_llm(raw)

        if not perguntas:
            return (
                f"Não consegui gerar perguntas sobre '{topico}'. "
                "Tente um tópico diferente ou verifique os materiais carregados."
            )

        self.quiz_session = QuizSession(topico=topico, perguntas=perguntas)
        return (
            f"🚀 Quiz iniciado sobre **{topico}**! "
            f"São {len(perguntas)} pergunta(s). Boa sorte!\n\n"
            + self._formatar_pergunta_quiz()
        )

    # ------------------------------------------------------------------
    # Ponto de entrada principal
    # ------------------------------------------------------------------

    def responder(self, user_message: str) -> str:
        """Processa a mensagem do usuário e retorna a resposta do JARVIS."""

        # ── Se há quiz em andamento, a mensagem é a resposta do aluno ──
        if self.quiz_session is not None:
            # Permite cancelar o quiz
            if user_message.strip().lower() in ("cancelar", "sair", "parar", "exit"):
                topico = self.quiz_session.topico
                self.quiz_session = None
                return f"Quiz sobre '{topico}' cancelado. Como posso ajudar?"
            return self._processar_resposta_quiz(user_message)

        self.historico.append({"role": "user", "content": user_message})

        # Verifica se o modelo quer chamar uma ferramenta
        chamada = decidir_ferramenta(user_message, TOOLS_SCHEMA)

        if chamada:
            tool_name = chamada["name"]
            arguments = chamada.get("arguments", {})
            print(f"[JARVIS] Chamando ferramenta: {tool_name}({arguments})")
            resultado_ferramenta = self._executar_ferramenta(tool_name, arguments)

            # Se o quiz foi iniciado pela ferramenta, retorna direto (sem reprocessar)
            if tool_name == "quiz_interativo":
                self.historico.append({"role": "assistant", "content": resultado_ferramenta})
                return resultado_ferramenta

            # Retorna o resultado da ferramenta para a LLM gerar resposta final
            messages_com_resultado = self.historico + [
                {
                    "role": "assistant",
                    "content": f"[Ferramenta {tool_name} retornou]: {resultado_ferramenta}",
                },
                {
                    "role": "user",
                    "content": "Com base no resultado acima, responda ao usuário de forma clara e amigável.",
                },
            ]
            resposta_final = gerar_resposta(messages_com_resultado)
        else:
            resposta_final = gerar_resposta(self.historico)

        self.historico.append({"role": "assistant", "content": resposta_final})
        return resposta_final


# ------------------------------------------------------------------
# Parser do output do LLM para formato de quiz
# ------------------------------------------------------------------

def _parsear_quiz_llm(raw: str) -> list[dict]:
    """
    Converte o texto bruto do LLM em lista de dicts de perguntas.
    Formato esperado por bloco (separado por ---):
        PERGUNTA: ...
        A) ...
        B) ...
        C) ...
        D) ...
        GABARITO: A
        EXPLICACAO: ...
    """
    perguntas = []
    blocos = raw.strip().split("---")
    for bloco in blocos:
        bloco = bloco.strip()
        if not bloco:
            continue
        q: dict = {"enunciado": "", "opcoes": [], "gabarito": "", "explicacao": ""}
        opcoes_map = {}
        for linha in bloco.splitlines():
            linha = linha.strip()
            if linha.upper().startswith("PERGUNTA:"):
                q["enunciado"] = linha.split(":", 1)[1].strip()
            elif linha.upper().startswith("GABARITO:"):
                q["gabarito"] = linha.split(":", 1)[1].strip().upper()
            elif linha.upper().startswith("EXPLICACAO:") or linha.upper().startswith("EXPLICAÇÃO:"):
                q["explicacao"] = linha.split(":", 1)[1].strip()
            elif linha and linha[0].upper() in "ABCD" and len(linha) > 2 and linha[1] == ")":
                letra = linha[0].upper()
                opcoes_map[letra] = linha
        q["opcoes"] = [opcoes_map[l] for l in "ABCD" if l in opcoes_map]
        if q["enunciado"] and q["gabarito"]:
            perguntas.append(q)
    return perguntas