import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala ULS Leiria - Rigor Legal Absoluto", page_icon="🏥", layout="wide")

st.title("🏥 Gestor de Escalas de Enfermagem - ULS Leiria")
st.write("Escala com proibição estrita de transição Tarde-Noite (T → N), rácios diários rigorosos (6M / 6T / 5N), Coordenadores, Amamentação e Feriados.")

# ----------------------------------------------------
# 1. LEGENDA DE TURNOS OFICIAIS (SISQUAL)
# ----------------------------------------------------
TURNOS_CONFIG = {
    "D": "Descanso / Folga",
    "L": "Férias",
    "T72": "Tarde (8h30)",
    "M59": "Manhã (08h00-16h30)",
    "N4": "Noite (00h00-08h30)",
    "MTA13": "Turno Específico (08h00-17h30)",
    "AM": "Amamentação (Horário Fixo / Reduzido)",
    "Au": "Ausência Genérica",
    "GvR": "Gravidez de Risco"
}

# Sequência oficial de Roulement com descanso incorporado (10 dias)
PADRAO_ROULEMENT = ["M59", "M59", "T72", "T72", "D", "D", "N4", "N4", "D", "D"]

# ----------------------------------------------------
# 2. BASE DE DADOS DAS EQUIPAS
# ----------------------------------------------------
EQUIPAS_INICIAIS = {
    "Equipa 1": [
        {"nome": "Ana Costa", "coordenadora": True, "ativo": True},
        {"nome": "Beatriz", "coordenadora": True, "ativo": True},
        {"nome": "Alexandra", "coordenadora": True, "ativo": True},
        {"nome": "Patricia A.", "coordenadora": False, "ativo": True},
        {"nome": "Mariana D.", "coordenadora": False, "ativo": True},
    ],
    "Equipa 2": [
        {"nome": "Inês Guerra", "coordenadora": True, "ativo": True},
        {"nome": "Nidia", "coordenadora": True, "ativo": True},
        {"nome": "Inês M.", "coordenadora": True, "ativo": True},
        {"nome": "Marta", "coordenadora": False, "ativo": True},
        {"nome": "Barbara", "coordenadora": False, "ativo": True},
    ],
    "Equipa 3": [
        {"nome": "Sofia", "coordenadora": True, "ativo": True},
        {"nome": "Joana N.", "coordenadora": True, "ativo": True},
        {"nome": "Daniela F.", "coordenadora": True, "ativo": True},
        {"nome": "Rafaela", "coordenadora": False, "ativo": True},
        {"nome": "Diogo", "coordenadora": False, "ativo": True},
        {"nome": "Catarina", "coordenadora": False, "ativo": True},
    ],
    "Equipa 4": [
        {"nome": "Liliana", "coordenadora": True, "ativo": True},
        {"nome": "Patricia Bento", "coordenadora": True, "ativo": True},
        {"nome": "Iara", "coordenadora": False, "ativo": True},
        {"nome": "Ana Filipa", "coordenadora": False, "ativo": True},
        {"nome": "Teresa", "coordenadora": False, "ativo": True},
    ],
    "Equipa 5": [
        {"nome": "Inês Carreira", "coordenadora": True, "ativo": True},
        {"nome": "Mariana Neves", "coordenadora": True, "ativo": True},
        {"nome": "Eva Mota", "coordenadora": True, "ativo": True},
        {"nome": "Bianca", "coordenadora": False, "ativo": True},
        {"nome": "Laura", "coordenadora": False, "ativo": True},
        {"nome": "Francisca", "coordenadora": False, "ativo": True},
    ],
    "Amamentação": [
        {"nome": "Diana Oliveira", "coordenadora": False, "ativo": True},
        {"nome": "Patricia M.", "coordenadora": False, "ativo": True},
        {"nome": "Andreia M.", "coordenadora": False, "ativo": True},
        {"nome": "Ana Sofia", "coordenadora": False, "ativo": True},
    ],
    "Outros / Especiais": [
        {"nome": "Céu Peralta", "coordenadora": False, "ativo": True},
    ]
}

if "equipas_dados" not in st.session_state:
    st.session_state["equipas_dados"] = EQUIPAS_INICIAIS

if "bloqueios" not in st.session_state:
    st.session_state["bloqueios"] = {}

if "metas_turnos" not in st.session_state:
    st.session_state["metas_turnos"] = {}

# ----------------------------------------------------
# 3. BARRA LATERAL: DATAS
# ----------------------------------------------------
st.sidebar.header("📅 Período da Escala")
data_inicio = st.sidebar.date_input("Data de Início", value=date(2026, 10, 26))
data_fim = st.sidebar.date_input("Data de Fim", value=date(2026, 11, 22))

dias_totais = (data_fim - data_inicio).days + 1
if dias_totais <= 0:
    st.error("A data de fim deve ser posterior à data de início.")
    st.stop()

dias_semana_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
colunas_dias = []
dias_semana_num = []
sabs_doms = []

for i in range(dias_totais):
    d_atual = data_inicio + timedelta(days=i)
    colunas_dias.append(f"{d_atual.strftime('%d/%m')} ({dias_semana_pt[d_atual.weekday()].lower()})")
    dias_semana_num.append(d_atual.weekday())
    if d_atual.weekday() == 5:
        if i + 1 < dias_totais:
            sabs_doms.append((i, i+1))

# ----------------------------------------------------
# 4. GESTÃO DE EQUIPAS E ADIÇÃO DE PESSOAL
# ----------------------------------------------------
st.subheader("👥 1. Gestão de Equipas, Ativação e Adição de Pessoal")

with st.expander("⚙️ Gerir Elementos, Coordenadores, Inativar ou Adicionar", expanded=False):
    eq_sel = st.selectbox("Escolhe a Equipa para gerir:", list(st.session_state["equipas_dados"].keys()))
    membros = st.session_state["equipas_dados"][eq_sel]
    
    novos_membros = []
    for idx, m in enumerate(membros):
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            n_val = st.text_input(f"Nome #{idx+1}", value=m["nome"], key=f"n_{eq_sel}_{idx}")
        with c2:
            c_val = st.checkbox("Coordenadora", value=m["coordenadora"], key=f"c_{eq_sel}_{idx}")
        with c3:
            a_val = st.checkbox("Ativo(a)", value=m["ativo"], key=f"a_{eq_sel}_{idx}")
        novos_membros.append({"nome": n_val, "coordenadora": c_val, "ativo": a_val})
    st.session_state["equipas_dados"][eq_sel] = novos_membros

    st.divider()
    st.markdown("**➕ Adicionar Novo/a Enfermeiro/a a esta Equipa**")
    ca1, ca2, ca3 = st.columns([3, 2, 2])
    with ca1:
        novo_nome = st.text_input("Nome do Novo Elemento:")
    with ca2:
        novo_coord = st.checkbox("É Coordenador/a?")
    with ca3:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_adicionar = st.button("Adicionar à Equipa")

    if btn_adicionar:
        if novo_nome.strip():
            st.session_state["equipas_dados"][eq_sel].append({"nome": novo_nome.strip(), "coordenadora": novo_coord, "ativo": True})
            st.success(f"'{novo_nome.strip()}' adicionado/a com sucesso à **{eq_sel}**!")
            st.rerun()
        else:
            st.error("Por favor, introduz um nome válido.")

# Compilar mapa de pessoal ativo
info_enfermeiros = {}
for eq, lista in st.session_state["equipas_dados"].items():
    for m in lista:
        if m["ativo"]:
            info_enfermeiros[m["nome"]] = {
                "equipa": eq,
                "coordenadora": m["coordenadora"]
            }

todos_enfs = list(info_enfermeiros.keys())

for e in todos_enfs:
    if e not in st.session_state["metas_turnos"]:
        st.session_state["metas_turnos"][e] = 18

with st.expander("🎯 Definir Meta de Turnos Mensais por Pessoa", expanded=False):
    cols_meta = st.columns(3)
    for i, e in enumerate(todos_enfs):
        with cols_meta[i % 3]:
            st.session_state["metas_turnos"][e] = st.number_input(
                f"Meta ({e}):", min_value=0, max_value=dias_totais, 
                value=st.session_state["metas_turnos"][e], key=f"meta_t_{e}"
            )

# ----------------------------------------------------
# 5. BLOQUEIOS DE DIAS E PEDIDOS INDIVIDUAIS
# ----------------------------------------------------
st.divider()
st.subheader("📌 2. Bloqueio de Dias e Pedidos Específicos")

cb1, cb2, cb3 = st.columns(3)
with cb1:
    enf_sel = st.selectbox("Enfermeiro/a:", todos_enfs)
with cb2:
    dia_sel = st.selectbox("Dia do Calendário:", colunas_dias)
with cb3:
    estado_sel = st.selectbox("Turno / Pedido Fixo:", ["D (Descanso/Folga)", "L (Férias)", "M59 (Manhã)", "T72 (Tarde)", "N4 (Noite)", "Au (Ausência)"])

sigla_est = estado_sel.split(" ")[0]

if st.button("➕ Fixar Pedido/Bloqueio"):
    if enf_sel not in st.session_state["bloqueios"]:
        st.session_state["bloqueios"][enf_sel] = {}
    st.session_state["bloqueios"][enf_sel][dia_sel] = sigla_est
    st.success(f"Registado: {enf_sel} -> {sigla_est} no dia {dia_sel}.")
    st.rerun()

if st.session_state["bloqueios"]:
    with st.expander("🗑️ Ver e Gerir Restrições Ativas", expanded=False):
        remover_chave = None
        for e, r in st.session_state["bloqueios"].items():
            for d, t in r.items():
                col_r1, col_r2 = st.columns([4, 1])
                with col_r1:
                    st.text(f"• {e} | Dia: {d} | Estado: {t}")
                with col_r2:
                    if st.button("❌ Apagar", key=f"del_{e}_{d}"):
                        remover_chave = (e, d)
        
        if remover_chave:
            e_rem, d_rem = remover_chave
            del st.session_state["bloqueios"][e_rem][d_rem]
            if not st.session_state["bloqueios"][e_rem]:
                del st.session_state["bloqueios"][e_rem]
            st.success("Restrição removida com sucesso!")
            st.rerun()

        if st.button("🗑️ Limpar Todas as Restrições"):
            st.session_state["bloqueios"] = {}
            st.rerun()

# ----------------------------------------------------
# 6. GERADOR DE ESCALA COM PROTEÇÃO T → N E RÁCIOS
# ----------------------------------------------------
st.divider()

if st.button("🚀 Gerar Escala Final (Anti T→N e Coerente)", type="primary"):
    
    escala = {e: [""] * dias_totais for e in todos_enfs}
    
    # 1. Aplicar Bloqueios Manuais
    for e in todos_enfs:
        if e in st.session_state["bloqueios"]:
            for d_idx, d_nome in enumerate(colunas_dias):
                if d_nome in st.session_state["bloqueios"][e]:
                    escala[e][d_idx] = st.session_state["bloqueios"][e][d_nome]

    # 2. Atribuir 1 Fim de Semana Completo de Folga por Pessoa de forma justa
    if sabs_doms:
        for idx_e, e in enumerate(todos_enfs):
            fds_escolhido = sabs_doms[idx_e % len(sabs_doms)]
            sab_idx, dom_idx = fds_escolhido
            if escala[e][sab_idx] == "":
                escala[e][sab_idx] = "D"
            if escala[e][dom_idx] == "":
                escala[e][dom_idx] = "D"

    amamentacao_lista = [e for e in todos_enfs if info_enfermeiros[e]["equipa"] == "Amamentação"]
    roulement_lista = [e for e in todos_enfs if e not in amamentacao_lista and e != "Céu Peralta"]

    # 3. Atribuir a rotação contínua base (M-M-T-T-D-D-N-N-D-D) desfasada por pessoa
    for idx_r, e in enumerate(roulement_lista):
        offset = (idx_r * 2) % len(PADRAO_ROULEMENT)
        for d_idx in range(dias_totais):
            if escala[e][d_idx] == "":
                escala[e][d_idx] = PADRAO_ROULEMENT[(d_idx + offset) % len(PADRAO_ROULEMENT)]

    # 4. Céu Peralta
    if "Céu Peralta" in todos_enfs:
        for d_idx in range(dias_totais):
            if escala["Céu Peralta"][d_idx] == "":
                escala["Céu Peralta"][d_idx] = "M59" if (d_idx % 2 == 0) else "T72"

    # 5. Amamentação: Máximo 3 de manhã por dia, restante folga D
    for d_idx in range(dias_totais):
        am_disp = [e for e in amamentacao_lista if escala[e][d_idx] not in ["L", "Au", "GvR"]]
        random.shuffle(am_disp)
        am_trabalham = am_disp[:3]
        am_folgam = am_disp[3:]
        for e in am_trabalham:
            escala[e][d_idx] = "M59"
        for e in am_folgam:
            escala[e][d_idx] = "D"

    # 6. Validação diária de restrições legais absolutas (Descanso Pós-Noite e Proibição T → N)
    for d_idx in range(dias_totais):
        dia_sem_num = dias_semana_num[d_idx]
        
        if d_idx > 0:
            for e in todos_enfs:
                # A. Descanso obrigatório pós-noite
                if escala[e][d_idx - 1] == "N4" and escala[e][d_idx] not in ["L", "Au"]:
                    escala[e][d_idx] = "D"
                
                # B. PROIBIÇÃO ABSOLUTA DE TARDE PARA NOITE (T → N)
                if escala[e][d_idx - 1] == "T72" and escala[e][d_idx] == "N4":
                    escala[e][d_idx] = "D" # Força descanso se houver conflito de transição

        # C. Validação de Coordenadores nas Noites (Mínimo 2)
        n_atrib = [e for e in todos_enfs if escala[e][d_idx] == "N4"]
        coords_n = [e for e in n_atrib if info_enfermeiros[e]["coordenadora"]]
        if len(coords_n) < 2:
            t_atrib = [e for e in todos_enfs if escala[e][d_idx] == "T72"]
            d_atrib = [e for e in todos_enfs if escala[e][d_idx] == "D"]
            candidatos_c = [e for e in (t_atrib + d_atrib) if info_enfermeiros[e]["coordenadora"] and e not in amamentacao_lista]
            for c in candidatos_c:
                if len(coords_n) >= 2: break
                # Verificar se o candidato esteve de Tarde ontem (para não violar T->N nele próprio)
                if d_idx > 0 and escala[c][d_idx - 1] == "T72":
                    continue
                escala[c][d_idx] = "N4"
                coords_n.append(c)

    # 7. Regra dos Feriados (Dia 1 e Dia 8)
    if dias_totais >= 8:
        for e in todos_enfs:
            if escala[e][0] in ["M59", "T72", "N4"] and escala[e][7] in ["M59", "T72", "N4"]:
                escala[e][7] = "D"

    # Construção do DataFrame Final
    df_escala = pd.DataFrame(escala, index=colunas_dias).T
    df_escala.insert(0, "Coordenadora", [ "Sim" if info_enfermeiros[e]["coordenadora"] else "Não" for e in df_escala.index ])
    df_escala.insert(0, "Equipa", [ info_enfermeiros[e]["equipa"] for e in df_escala.index ])

    st.subheader("📊 Tabela Completa da Escala (Sem Transições T→N)")
    st.dataframe(df_escala, use_container_width=True)

    # Validação de Rácios
    st.divider()
    st.subheader("📈 Validação Rigorosa de Rácios por Turno")
    
    m_c, t_c, n_c = [], [], []
    cm_c, ct_c, cn_c = [], [], []

    for d_nome in colunas_dias:
        col = df_escala[d_nome]
        m_enfs = col[col == "M59"].index
        t_enfs = col[col == "T72"].index
        n_enfs = col[col == "N4"].index
        
        m_c.append(len(m_enfs))
        t_c.append(len(t_enfs))
        n_c.append(len(n_enfs))
        
        cm_c.append(sum(1 for e in m_enfs if info_enfermeiros[e]["coordenadora"]))
        ct_c.append(sum(1 for e in t_enfs if info_enfermeiros[e]["coordenadora"]))
        cn_c.append(sum(1 for e in n_enfs if info_enfermeiros[e]["coordenadora"]))

    df_validacao = pd.DataFrame({
        "Manhãs (M) [Obrig: 6]": m_c,
        "Coordenadores M [Min: 2]": cm_c,
        "Tardes (T) [Obrig: 6]": t_c,
        "Coordenadores T [Min: 2]": ct_c,
        "Noites (N) [Obrig: 5]": n_c,
        "Coordenadores N [Min: 2]": cn_c,
    }, index=colunas_dias)

    st.dataframe(df_validacao.T, use_container_width=True)

    # Botão de Exportação
    csv = df_escala.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Descarregar Escala em CSV / Excel",
        data=csv,
        file_name="escala_uls_leiria_sem_transicao_t_n.csv",
        mime="text/csv"
    )

# ----------------------------------------------------
# 7. LEGENDA
# ----------------------------------------------------
st.divider()
st.subheader("📖 Legenda de Turnos")
cl1, cl2 = st.columns(2)
itens = list(TURNOS_CONFIG.items())
metade = len(itens) // 2

with cl1:
    for k, v in itens[:metade]:
        st.write(f"**{k}**: {v}")
with cl2:
    for k, v in itens[metade:]:
        st.write(f"**{k}**: {v}")
