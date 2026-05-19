"""Interface Streamlit do JARVIS Acadêmico."""

import streamlit as st
import json
from pathlib import Path
from datetime import date

# --- Configuração da página ---
st.set_page_config(
    page_title="JARVIS Acadêmico",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS customizado ---
st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #01696f; margin-bottom: 0; }
    .sub-header  { font-size: 1rem; color: #7a7974; margin-top: 0; margin-bottom: 1.5rem; }
    .tool-badge  { background: #cedcd8; color: #01696f; padding: 2px 10px;
                   border-radius: 999px; font-size: 0.78rem; font-weight: 600; }
    .log-entry   { background: #f3f0ec; border-radius: 8px; padding: 8px 12px;
                   margin-bottom: 6px; font-size: 0.82rem; font-family: monospace; }
    .msg-user    { background: #e6e4df; border-radius: 12px 12px 4px 12px;
                   padding: 10px 14px; margin: 6px 0; max-width: 80%; margin-left: auto; }
    .msg-jarvis  { background: #f9f8f5; border: 1px solid #dcd9d5; border-radius: 12px 12px 12px 4px;
                   padding: 10px 14px; margin: 6px 0; max-width: 85%; }
    .quiz-card   { background: #f0f7f7; border: 2px solid #01696f; border-radius: 12px;
                   padding: 20px 24px; margin: 12px 0; }
    .quiz-progress { font-size: 0.82rem; color: #7a7974; margin-bottom: 8px; }
    .opcao-btn   { width: 100%; text-align: left; margin: 4px 0; }
    .feedback-correct   { background: #d4dfcc; border-radius: 8px; padding: 10px 14px; color: #1e3f0a; }
    .feedback-incorrect { background: #ddc9d0; border-radius: 8px; padding: 10px 14px; color: #561740; }
</style>
""", unsafe_allow_html=True)


# --- Inicialização do estado da sessão ---
def _init_state():
    defaults = {
        "rag_carregado": False,
        "agente": None,
        "vectorstore": None,
        "historico_chat": [],
        # Quiz UI state
        "quiz_feedback": None,
        "quiz_respondeu": False,
        "quiz_relatorio_pendente": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# --- Helper: referência única ao agente ---
def _agente():
    """Retorna o agente do session_state (única fonte de verdade)."""
    return st.session_state.get("agente")


# --- Carregamento do agente (lazy) ---
@st.cache_resource(show_spinner="Carregando modelo Gemma 12B...")
def _carregar_agente():
    from main import inicializar_rag
    from src.agent import JarvisAgent
    vectorstore = inicializar_rag()
    agente = JarvisAgent(vectorstore=vectorstore)
    return agente, vectorstore


def _cancelar_quiz():
    """Cancela o quiz ativo e limpa todos os estados relacionados."""
    ag = _agente()
    if ag and ag.quiz_session:
        topico = ag.quiz_session.topico
        ag.quiz_session = None
        st.session_state["quiz_feedback"] = None
        st.session_state["quiz_respondeu"] = False
        st.session_state["quiz_relatorio_pendente"] = None
        return topico
    return None


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown('<p class="main-header">🎓 JARVIS</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Assistente Acadêmico Inteligente</p>', unsafe_allow_html=True)
    st.divider()

    if not st.session_state["rag_carregado"]:
        if st.button("▶ Iniciar JARVIS", use_container_width=True, type="primary"):
            with st.spinner("Carregando modelo e documentos..."):
                agente_obj, vs = _carregar_agente()
                st.session_state["agente"] = agente_obj
                st.session_state["vectorstore"] = vs
                st.session_state["rag_carregado"] = True
            st.success("JARVIS pronto!")
            st.rerun()
    else:
        ag_sidebar = _agente()
        if ag_sidebar and ag_sidebar.quiz_session:
            sess_sb = ag_sidebar.quiz_session
            st.warning(f"🧠 Quiz ativo: {sess_sb.topico}")
            total_sb = len(sess_sb.perguntas)
            idx_sb = sess_sb.indice_atual
            st.progress(idx_sb / total_sb, text=f"{idx_sb}/{total_sb} respondidas")
            # ── FIX: usa _cancelar_quiz() — mesma função usada no body ──
            if st.button("🚫 Cancelar quiz", use_container_width=True):
                topico_cancelado = _cancelar_quiz()
                if topico_cancelado:
                    st.session_state["historico_chat"].append({
                        "role": "assistant",
                        "content": f"Quiz sobre **{topico_cancelado}** cancelado. Como posso ajudar?",
                    })
                st.rerun()
        else:
            st.success("✅ JARVIS ativo")

    st.divider()
    st.markdown("### 🔧 Ferramentas disponíveis")
    ferramentas = [
        ("📅", "consultar_agenda"),
        ("📋", "listar_tarefas"),
        ("➕", "adicionar_tarefa"),
        ("✅", "concluir_tarefa"),
        ("📚", "buscar_material_rag"),
        ("✏️", "gerar_exercicios"),
        ("🧠", "quiz_interativo"),
    ]
    for icone, nome in ferramentas:
        st.markdown(f"{icone} `{nome}`")

    st.divider()
    st.markdown("### 📁 Documentos carregados")
    docs_path = Path("data/docs")
    docs = list(docs_path.glob("*.pdf")) + list(docs_path.glob("*.txt"))
    if docs:
        for d in docs:
            st.markdown(f"- {d.name}")
    else:
        st.warning("Nenhum documento em data/docs/")

    st.divider()
    if st.button("🗑 Limpar conversa", use_container_width=True):
        st.session_state["historico_chat"] = []
        _cancelar_quiz()
        st.rerun()


# ==================== ABAS PRINCIPAIS ====================
tab_chat, tab_agenda, tab_tarefas, tab_logs = st.tabs(
    ["💬 Chat", "📅 Agenda", "📋 Tarefas", "📊 Logs"]
)


# ==================== ABA CHAT ====================
with tab_chat:
    st.markdown("### 💬 Converse com o JARVIS")

    # ── FIX: sempre lê o agente via session_state (única fonte de verdade) ──
    agente = _agente()
    quiz_ativo = agente is not None and agente.quiz_session is not None

    # --- Histórico de mensagens ---
    with st.container():
        if not st.session_state["historico_chat"]:
            st.info("👋 Olá! Inicie o JARVIS no menu lateral e faça sua primeira pergunta.")
        for msg in st.session_state["historico_chat"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="msg-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-jarvis">🎓 {msg["content"]}</div>', unsafe_allow_html=True)

    st.divider()

    # ======================================================
    # MODO QUIZ — UI dedicada com botões de múltipla escolha
    # ======================================================
    # A MELHOR PRÁTICA: Depender do objeto existir, em vez de uma flag solta.
    quiz_ativo = st.session_state.get("quiz_ativo", False)

    if quiz_ativo and agente.quiz_session is not None:
        sess = agente.quiz_session
        q = sess.pergunta_atual
        total = len(sess.perguntas)
        idx = sess.indice_atual

        st.markdown(
            f'<div class="quiz-progress">Pergunta {idx + 1} de {total} · Tópico: {sess.topico}</div>',
            unsafe_allow_html=True,
        )
        st.progress(idx / total)

        with st.container():
            st.markdown(f'<div class="quiz-card"><b>{q["enunciado"]}</b></div>', unsafe_allow_html=True)

        # --- Feedback da resposta anterior ---
        if st.session_state.get("quiz_feedback"):
            fb = st.session_state["quiz_feedback"]
            css_class = "feedback-correct" if fb["correto"] else "feedback-incorrect"
            icon = "✅" if fb["correto"] else "❌"
            st.markdown(
                f'<div class="{css_class}">{icon} {fb["texto"]}</div>',
                unsafe_allow_html=True,
            )

            quiz_terminou = sess.concluido
            label_btn = "🏁 Ver resultado" if quiz_terminou else "➡️ Próxima pergunta"

            if st.button(label_btn, type="primary", use_container_width=True):
                st.session_state["quiz_feedback"] = None
                st.session_state["quiz_respondeu"] = False
                
                # LÓGICA DE ENCERRAMENTO (Gatilho)
                if quiz_terminou:
                    relatorio = sess.relatorio_final()
                    agente.quiz_session = None
                    st.session_state["quiz_ativo"] = False # CORREÇÃO 1: Desliga a flag
                    st.session_state["historico_chat"].append(
                        {"role": "assistant", "content": relatorio}
                    )
                st.rerun()

        # --- Aguardando Resposta ---
        elif not st.session_state.get("quiz_respondeu", False):
            
            if st.button("🚫 Cancelar quiz", key="cancel_quiz_body"):
                topico_cancelado = _cancelar_quiz()
                st.session_state["quiz_ativo"] = False # Garante o cancelamento da flag
                if topico_cancelado:
                    st.session_state["historico_chat"].append({
                        "role": "assistant",
                        "content": f"Quiz sobre **{topico_cancelado}** cancelado. Como posso ajudar?",
                    })
                st.rerun()

            # Botões Múltipla Escolha
            if q.get("opcoes"):
                cols = st.columns(2)
                letras = ["A", "B", "C", "D"]
                for i, opcao in enumerate(q["opcoes"]):
                    with cols[i % 2]:
                        if st.button(opcao, key=f"opcao_{idx}_{i}", use_container_width=True):
                            letra_escolhida = letras[i]
                            gabarito = q.get("gabarito", "").strip().upper()
                            correto = letra_escolhida == gabarito[:1]
                            explicacao = q.get("explicacao", "")
                            texto_fb = (
                                f"Correto! {explicacao}" if correto
                                else f"Incorreto. A resposta certa era **{gabarito}**. {explicacao}"
                            )
                            sess.registrar_resposta(letra_escolhida, correto, explicacao)
                            st.session_state["quiz_feedback"] = {"correto": correto, "texto": texto_fb}
                            st.session_state["quiz_respondeu"] = True
                            st.rerun()
            
            # Formulário Questão Aberta
            else:
                with st.form("quiz_open_form", clear_on_submit=True):
                    resposta_aberta = st.text_area("Sua resposta:", key="quiz_open_input")
                    if st.form_submit_button("Enviar resposta", type="primary"):
                        if resposta_aberta.strip():
                            # CORREÇÃO 2: Processa a resposta e passa pela mesma lógica de finalização
                            resultado_str = agente._processar_resposta_quiz(resposta_aberta)
                            
                            st.session_state["historico_chat"].append(
                                {"role": "assistant", "content": resultado_str}
                            )
                            
                            # Verifica se processar_resposta concluiu o quiz internamente
                            if sess.concluido:
                                relatorio = sess.relatorio_final()
                                agente.quiz_session = None
                                st.session_state["quiz_ativo"] = False
                                st.session_state["historico_chat"].append(
                                    {"role": "assistant", "content": relatorio}
                                )
                            
                            st.session_state["quiz_feedback"] = None
                            st.session_state["quiz_respondeu"] = False
                            st.rerun()

    # ======================================================
    # MODO NORMAL — input de texto
    # ======================================================
    else:
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_btn = st.columns([5, 1])
            with col_input:
                user_input = st.text_input(
                    "Mensagem",
                    placeholder="Ex: O que tenho hoje? | Explique embeddings | Quiz sobre redes neurais",
                    label_visibility="collapsed",
                )
            with col_btn:
                enviado = st.form_submit_button("Enviar", use_container_width=True)

        if enviado and user_input.strip():
            if not st.session_state["rag_carregado"]:
                st.error("Inicie o JARVIS primeiro clicando em '▶ Iniciar JARVIS' no menu lateral.")
            else:
                st.session_state["historico_chat"].append({"role": "user", "content": user_input})
                with st.spinner("JARVIS pensando..."):
                    resposta = agente.responder(user_input)
                st.session_state["historico_chat"].append({"role": "assistant", "content": resposta})
                st.rerun()

        st.markdown("**Sugestões rápidas:**")
        sugestoes = [
            "O que tenho hoje?",
            "Quais tarefas estão pendentes?",
            "Explique regressão logística",
            "Gere 3 exercícios sobre embeddings",
            "Quiz sobre redes neurais",
        ]
        cols = st.columns(len(sugestoes))
        for i, sug in enumerate(sugestoes):
            with cols[i]:
                if st.button(sug, key=f"sug_{i}", use_container_width=True):
                    if st.session_state["rag_carregado"]:
                        st.session_state["historico_chat"].append({"role": "user", "content": sug})
                        with st.spinner("JARVIS pensando..."):
                            resp = agente.responder(sug)
                        st.session_state["historico_chat"].append({"role": "assistant", "content": resp})
                        st.rerun()


# ==================== ABA AGENDA ====================
with tab_agenda:
    st.markdown("### 📅 Agenda Acadêmica")

    agenda_path = Path("data/agenda.json")
    if agenda_path.exists():
        agenda = json.loads(agenda_path.read_text(encoding="utf-8"))
    else:
        agenda = []

    col_filtro, col_add = st.columns([2, 1])
    with col_filtro:
        periodo = st.selectbox("Filtrar por período:", ["Todos", "Hoje", "Esta semana"])

    from datetime import timedelta
    hoje_str = date.today().isoformat()
    semana = [(date.today() + timedelta(days=i)).isoformat() for i in range(7)]

    if periodo == "Hoje":
        eventos = [e for e in agenda if e.get("data") == hoje_str]
    elif periodo == "Esta semana":
        eventos = [e for e in agenda if e.get("data") in semana]
    else:
        eventos = agenda

    if eventos:
        for e in sorted(eventos, key=lambda x: (x.get("data", ""), x.get("hora", ""))):
            tipo_icons = {"prova": "🔴", "aula": "📗", "trabalho": "🟡", "seminario": "🔵"}
            icone = tipo_icons.get(e.get("tipo", ""), "📌")
            with st.expander(f"{icone} {e.get('data')} {e.get('hora', '')} — {e.get('disciplina', '')}"):
                st.markdown(f"**Tipo:** {e.get('tipo', '').capitalize()}")
                st.markdown(f"**Disciplina:** {e.get('disciplina', '')}")
                st.markdown(f"**Descrição:** {e.get('descricao', '')}")
    else:
        st.info("Nenhum evento encontrado para o período selecionado.")

    st.divider()
    st.markdown("#### ➕ Adicionar evento")
    with st.form("form_agenda"):
        c1, c2, c3 = st.columns(3)
        with c1:
            nova_data = st.date_input("Data", value=date.today())
        with c2:
            nova_hora = st.time_input("Hora")
        with c3:
            novo_tipo = st.selectbox("Tipo", ["aula", "prova", "trabalho", "seminario"])
        nova_disc = st.text_input("Disciplina")
        nova_desc = st.text_input("Descrição")
        if st.form_submit_button("Adicionar evento"):
            if nova_disc and nova_desc:
                novo_id = max((e["id"] for e in agenda), default=0) + 1
                agenda.append({
                    "id": novo_id,
                    "data": nova_data.isoformat(),
                    "hora": nova_hora.strftime("%H:%M"),
                    "tipo": novo_tipo,
                    "disciplina": nova_disc,
                    "descricao": nova_desc,
                })
                agenda_path.write_text(json.dumps(agenda, ensure_ascii=False, indent=2), encoding="utf-8")
                st.success("Evento adicionado!")
                st.rerun()


# ==================== ABA TAREFAS ====================
with tab_tarefas:
    st.markdown("### 📋 Tarefas Acadêmicas")

    tarefas_path = Path("data/tarefas.json")
    if tarefas_path.exists():
        tarefas = json.loads(tarefas_path.read_text(encoding="utf-8"))
    else:
        tarefas = []

    filtro_status = st.radio("Filtrar:", ["Todas", "Pendentes", "Concluídas"], horizontal=True)
    if filtro_status == "Pendentes":
        tarefas_vis = [t for t in tarefas if t.get("status") == "pendente"]
    elif filtro_status == "Concluídas":
        tarefas_vis = [t for t in tarefas if t.get("status") == "concluida"]
    else:
        tarefas_vis = tarefas

    if tarefas_vis:
        for t in tarefas_vis:
            col_check, col_info = st.columns([1, 10])
            concluida = t.get("status") == "concluida"
            with col_check:
                marcar = st.checkbox("", value=concluida, key=f"task_{t['id']}")
                if marcar and not concluida:
                    for item in tarefas:
                        if item["id"] == t["id"]:
                            item["status"] = "concluida"
                    tarefas_path.write_text(json.dumps(tarefas, ensure_ascii=False, indent=2), encoding="utf-8")
                    st.rerun()
            with col_info:
                prazo = f" | ⏰ {t['prazo']}" if t.get("prazo") else ""
                disc = f" | 📘 {t['disciplina']}" if t.get("disciplina") else ""
                texto = f"~~{t['titulo']}~~" if concluida else t['titulo']
                st.markdown(f"**#{t['id']}** {texto}{disc}{prazo}")
    else:
        st.info("Nenhuma tarefa encontrada.")

    st.divider()
    st.markdown("#### ➕ Nova tarefa")
    with st.form("form_tarefa"):
        c1, c2, c3 = st.columns(3)
        with c1:
            novo_titulo = st.text_input("Título da tarefa")
        with c2:
            novo_prazo = st.date_input("Prazo (opcional)", value=None)
        with c3:
            nova_disc_t = st.text_input("Disciplina (opcional)")
        if st.form_submit_button("Adicionar tarefa"):
            if novo_titulo.strip():
                novo_id_t = max((t["id"] for t in tarefas), default=0) + 1
                tarefas.append({
                    "id": novo_id_t,
                    "titulo": novo_titulo,
                    "prazo": novo_prazo.isoformat() if novo_prazo else None,
                    "disciplina": nova_disc_t or None,
                    "status": "pendente",
                })
                tarefas_path.write_text(json.dumps(tarefas, ensure_ascii=False, indent=2), encoding="utf-8")
                st.success(f"Tarefa '{novo_titulo}' adicionada!")
                st.rerun()


# ==================== ABA LOGS ====================
with tab_logs:
    st.markdown("### 📊 Logs de Tool Calling")
    st.caption("Registro de todas as ferramentas chamadas pelo sistema.")

    log_path = Path("logs/tool_calls.jsonl")
    if log_path.exists() and log_path.stat().st_size > 0:
        linhas = log_path.read_text(encoding="utf-8").strip().splitlines()
        registros = [json.loads(l) for l in linhas if l.strip()]
        registros_rev = list(reversed(registros))

        from collections import Counter
        contagem = Counter(r["tool"] for r in registros)
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total de chamadas", len(registros))
        col_m2.metric("Ferramentas únicas", len(contagem))
        col_m3.metric("Ferramenta mais usada", contagem.most_common(1)[0][0] if contagem else "—")

        st.divider()

        todas_tools = ["Todas"] + sorted(contagem.keys())
        filtro_tool = st.selectbox("Filtrar por ferramenta:", todas_tools)

        exibir = registros_rev if filtro_tool == "Todas" else [r for r in registros_rev if r["tool"] == filtro_tool]

        for reg in exibir[:50]:
            with st.expander(f"🔧 `{reg['tool']}` — {reg['timestamp'][:19].replace('T', ' ')}"):
                st.markdown("**Entrada:**")
                st.json(reg["input"])
                st.markdown("**Saída:**")
                st.code(str(reg["output"]), language="text")
    else:
        st.info("Nenhum log ainda. Interaja com o JARVIS para gerar registros.")