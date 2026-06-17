"""Interface Streamlit do JARVIS Acadêmico."""

import streamlit as st
import json
from pathlib import Path
from datetime import date
from src.rag.pdf_converter import converter_pdf
from src.config import DOCSMD_PATH

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
    .upload-box  { background: #f0f7f7; border: 1px dashed #01696f; border-radius: 10px;
                   padding: 12px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)


# --- Inicialização do estado da sessão ---
def _init_state():
    defaults = {
        "rag_carregado": False,
        "agente": None,
        "vectorstore": None,
        "historico_chat": [],
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
    return st.session_state.get("agente")


# --- Carregamento do agente (lazy) ---
@st.cache_resource(show_spinner="Carregando modelo...")
def _carregar_agente():
    from main import inicializar_rag
    from src.agent import JarvisAgent

    vectorstore, bm25 = inicializar_rag()   
    agente = JarvisAgent(vectorstore=vectorstore, bm25_store=bm25)
    return agente, vectorstore


def _cancelar_quiz():
    ag = _agente()
    if ag and ag.quiz_session:
        topico = ag.quiz_session.topico
        ag.quiz_session = None
        st.session_state["quiz_feedback"] = None
        st.session_state["quiz_respondeu"] = False
        st.session_state["quiz_relatorio_pendente"] = None
        return topico
    return None


# ---------------------------------------------------------------------------
# Metadados padrão por disciplina detectada no nome do arquivo
# ---------------------------------------------------------------------------

_DISCIPLINAS_META: dict[str, dict] = {
    "mc102": {
        "disciplina": "MC102 — Algoritmos e Programação de Computadores",
        "fonte": "IC/Unicamp — Prof. Alexandre Xavier Falcão",
        "fonte_url": "https://www.ic.unicamp.br/~afalcao/mc102/",
        "licenca": "Uso acadêmico",
    },
    "mc202": {
        "disciplina": "MC202 — Estruturas de Dados",
        "fonte": "IC/Unicamp",
        "fonte_url": "",
        "licenca": "Uso acadêmico",
    },
}


def _inferir_meta(filename: str) -> dict:
    """Retorna metadados de disciplina com base em palavras-chave no nome do arquivo."""
    lower = filename.lower()
    for chave, meta in _DISCIPLINAS_META.items():
        if chave in lower:
            return meta
    return {}


# ---------------------------------------------------------------------------
# Processar PDF → salva em data/docs/ e converte para data/docsmd/
# ---------------------------------------------------------------------------

def processar_upload_pdf(
    uploaded_file,
    disciplina: str = "",
    fonte: str = "",
    fonte_url: str = "",
    licenca: str = "",
) -> str:
    """
    Recebe um UploadedFile do Streamlit, persiste o PDF original em
    data/docs/ e converte para Markdown estruturado em data/docsmd/.
    Retorna o caminho do .md gerado.
    """
    docs_path = Path("data/docs")
    docs_path.mkdir(parents=True, exist_ok=True)

    # Salva o PDF original em data/docs/
    pdf_dest = docs_path / uploaded_file.name
    pdf_dest.write_bytes(uploaded_file.read())

    # Infere metadados pelo nome do arquivo se não fornecidos explicitamente
    if not disciplina:
        meta = _inferir_meta(uploaded_file.name)
        disciplina = meta.get("disciplina", "")
        fonte = meta.get("fonte", fonte)
        fonte_url = meta.get("fonte_url", fonte_url)
        licenca = meta.get("licenca", licenca)

    try:
        md_path, meta_path = converter_pdf(
            pdf_path=pdf_dest,
            out_dir=DOCSMD_PATH,
            disciplina=disciplina,
            fonte=fonte,
            fonte_url=fonte_url,
            licenca=licenca,
        )
        return str(md_path)
    except ValueError as e:
        pdf_dest.unlink(missing_ok=True)
        raise RuntimeError(f"Não foi possível extrair texto do PDF: {e}") from e


# ---------------------------------------------------------------------------
# Helper: apaga .md, .metadata.json e o PDF original de um documento
# ---------------------------------------------------------------------------

def _remover_documento(stem: str, docsmd_path: Path, docs_path: Path) -> None:
    """Remove os três arquivos associados a um documento (md, metadata, pdf)."""

    # 1. Remove o .md
    md_file = docsmd_path / (stem + ".md")
    md_file.unlink(missing_ok=True)

    # 2. Tenta descobrir o nome original do PDF a partir do metadata
    meta_file = docsmd_path / (stem + ".metadata.json")
    pdf_nome = stem + ".pdf"  # fallback: mesmo nome do stem
    if meta_file.exists():
        try:
            m = json.loads(meta_file.read_text(encoding="utf-8"))
            # source_pdf pode conter apenas o nome ou o caminho completo
            source = m.get("source_pdf", "")
            if source:
                pdf_nome = Path(source).name
        except Exception:
            pass
        meta_file.unlink(missing_ok=True)
    else:
        meta_file.unlink(missing_ok=True)  # garante remoção mesmo se o try pulou

    # 3. Remove o PDF original em data/docs/
    pdf_original = docs_path / pdf_nome
    pdf_original.unlink(missing_ok=True)


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown('<p class="main-header">🎓 JARVIS</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Assistente Acadêmico Inteligente</p>', unsafe_allow_html=True)
    st.divider()
    
     # ── UPLOAD DE PDFs ────────────────────────────────────────────────
    docs_path = Path("data/docs")
    docs_path.mkdir(parents=True, exist_ok=True)
    docsmd_path = Path("data/docsmd")
    docsmd_path.mkdir(parents=True, exist_ok=True)

    # ── BOTÃO INICIAR ────────────────────────────────────────────────
    if not st.session_state["rag_carregado"]:
        mds_disponiveis = list(docsmd_path.glob("*.md"))
        if not mds_disponiveis:
            st.warning(
                "📂 Nenhum documento convertido ainda. "
                "Envie ao menos um PDF acima antes de iniciar."
            )
        if st.button(
            "▶ Iniciar JARVIS",
            use_container_width=True,
            type="primary",
            disabled=len(mds_disponiveis) == 0,
        ):
            with st.spinner("Carregando modelo e indexando documentos..."):
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

    st.markdown("### 📤 Enviar documentos (PDF)")
    st.caption(
        "Os PDFs serão salvos em `data/docs/` e automaticamente "
        "convertidos para Markdown estruturado em `data/docsmd/`."
    )

    with st.expander("⚙️ Metadados do documento (opcional)", expanded=False):
        meta_disciplina = st.text_input(
            "Disciplina",
            placeholder="Ex: MC102 — Algoritmos e Programação de Computadores",
            key="meta_disciplina",
        )
        meta_fonte = st.text_input(
            "Fonte",
            placeholder="Ex: IC/Unicamp — Prof. Alexandre Xavier Falcão",
            key="meta_fonte",
        )
        meta_url = st.text_input(
            "URL da fonte",
            placeholder="https://www.ic.unicamp.br/~afalcao/mc102/",
            key="meta_url",
        )
        meta_licenca = st.text_input(
            "Licença",
            placeholder="Ex: CC BY-NC-SA 4.0",
            key="meta_licenca",
        )

    uploaded = st.file_uploader("Carregar PDF", type=["pdf"])
    if uploaded:
        with st.spinner("Convertendo PDF..."):
            try:
                md_path = processar_upload_pdf(
                    uploaded,
                    disciplina=meta_disciplina,
                    fonte=meta_fonte,
                    fonte_url=meta_url,
                    licenca=meta_licenca,
                )
                st.success(f"Documento carregado: `{Path(md_path).name}`")
                st.session_state["rag_indexado"] = False
            except RuntimeError as e:
                st.error(str(e))

    st.divider()
    st.markdown("### 📁 Documentos")

    mds_sidebar = sorted(docsmd_path.glob("*.md"))
    if mds_sidebar:
        for d in mds_sidebar:
            # mostra metadados se disponíveis
            meta_file = docsmd_path / (d.stem + ".metadata.json")
            tooltip = d.stem
            if meta_file.exists():
                try:
                    m = json.loads(meta_file.read_text(encoding="utf-8"))
                    disciplina_meta = m.get("disciplina", "")
                    pages = m.get("num_pages", "")
                    tooltip = f"{disciplina_meta} | {pages}p" if disciplina_meta else d.stem
                except Exception:
                    pass

            col_d, col_x = st.columns([8, 1])
            with col_d:
                st.markdown(f"🟢 **{d.stem}** `{tooltip}`")
            with col_x:
                if st.button("✕", key=f"del_{d.name}", help=f"Remover {d.stem}"):
                    _remover_documento(d.stem, docsmd_path, docs_path)
                    if st.session_state["rag_carregado"]:
                        st.cache_resource.clear()
                        st.session_state["rag_carregado"] = False
                        st.session_state["agente"] = None
                        st.session_state["vectorstore"] = None
                    st.rerun()
        st.caption("🟢 convertido para Markdown")
    else:
        st.warning("Nenhum .md em data/docsmd/")

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

    agente = _agente()

    with st.container():
        if not st.session_state["historico_chat"]:
            st.info("👋 Olá! Envie seus PDFs no menu lateral, inicie o JARVIS e faça sua primeira pergunta.")
        for msg in st.session_state["historico_chat"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="msg-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-jarvis">🎓 {msg["content"]}</div>', unsafe_allow_html=True)

    st.divider()

    quiz_ativo = st.session_state.get("quiz_ativo", False)

    if quiz_ativo and agente is not None and agente.quiz_session is not None:
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

        if st.session_state.get("quiz_feedback"):
            fb = st.session_state["quiz_feedback"]
            css_class = "feedback-correct" if fb["correto"] else "feedback-incorrect"
            icon = "✅" if fb["correto"] else "❌"
            st.markdown(f'<div class="{css_class}">{icon} {fb["texto"]}</div>', unsafe_allow_html=True)

            quiz_terminou = sess.concluido
            label_btn = "🏁 Ver resultado" if quiz_terminou else "➡️ Próxima pergunta"

            if st.button(label_btn, type="primary", use_container_width=True):
                st.session_state["quiz_feedback"] = None
                st.session_state["quiz_respondeu"] = False
                if quiz_terminou:
                    relatorio = sess.relatorio_final()
                    agente.quiz_session = None
                    st.session_state["quiz_ativo"] = False
                    st.session_state["historico_chat"].append(
                        {"role": "assistant", "content": relatorio}
                    )
                st.rerun()

        elif not st.session_state.get("quiz_respondeu", False):
            if st.button("🚫 Cancelar quiz", key="cancel_quiz_body"):
                topico_cancelado = _cancelar_quiz()
                st.session_state["quiz_ativo"] = False
                if topico_cancelado:
                    st.session_state["historico_chat"].append({
                        "role": "assistant",
                        "content": f"Quiz sobre **{topico_cancelado}** cancelado. Como posso ajudar?",
                    })
                st.rerun()

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
            else:
                with st.form("quiz_open_form", clear_on_submit=True):
                    resposta_aberta = st.text_area("Sua resposta:", key="quiz_open_input")
                    if st.form_submit_button("Enviar resposta", type="primary"):
                        if resposta_aberta.strip():
                            resultado_str = agente._processar_resposta_quiz(resposta_aberta)
                            st.session_state["historico_chat"].append(
                                {"role": "assistant", "content": resultado_str}
                            )
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
    else:
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_btn = st.columns([5, 1])
            with col_input:
                user_input = st.text_input(
                    "Mensagem",
                    placeholder="Digite sua pergunta ou comando para o JARVIS aqui...",
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
            "Quais provas tenho agendadas?",
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

    col_filtro, _ = st.columns([2, 1])
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
                marcar = st.checkbox(
                    "Concluída",
                    value=concluida,
                    key=f"task_{t['id']}",
                    label_visibility="collapsed",)
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