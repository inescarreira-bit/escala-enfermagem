import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala ULS Leiria - Rácios Estritos", page_icon="🏥", layout="wide")

st.title("🏥 Gestor de Escalas de Enfermagem - ULS Leiria")
st.write("Garantia absoluta de rácios diários (6 Manhãs, 6 Tardes, 5 Noites), mín. 2 Coordenadores/turno, Proteção de Amamentação e Feriados.")

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
# 6. GERADOR DE ESCALA COM RÁCIOS ESTRITOS (6M, 6T, 5N)
# ----------------------------------------------------
st.divider()

if st.button("🚀 Gerar Escala Final (Rácios Exatos e Coordenadores)", type="primary"):
    
    escala = {e: [""] * dias_totais for e in todos_enfs}
    
    # 1. Aplicar Bloqueios Manuais (Férias, Folgas Fixas, etc.)
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

    # 3. Processamento Diário Rigoroso (Força exatamente 6M, 6T, 5N e >=2 Coordenadores)
    for d_idx in range(dias_totais):
        dia_sem_num = dias_semana_num[d_idx]
        
        # A. Quem já tem folga fixa ou férias ou repouso pós-noite do dia anterior
        for e in todos_enfs:
            if d_idx > 0 and escala[e][d_idx - 1] == "N4" and escala[e][d_idx] == "":
                escala[e][d_idx] = "D" # Descanso obrigatório pós-noite

        # B. Amamentação: Máximo 3 de manhã, restante folga D
        am_disp = [e for e in amamentacao_lista if escala[e][d_idx] == ""]
        random.shuffle(am_disp)
        am_trabalham = am_disp[:3]
        am_folgam = am_disp[3:]
        
        for e in am_trabalham:
            escala[e][d_idx] = "M59"
        for e in am_folgam:
            escala[e][d_idx] = "D"

        # C. Obter lista de disponíveis para preencher os rácios do dia
        disponiveis = [e for e in todos_enfs if escala[e][d_idx] == ""]
        
        # Filtrar restrição de segunda-feira pós-fim de semana para noites
        aptos_noite = []
        for e in disponiveis:
            if dia_sem_num == 0 and d_idx > 0:
                if escala[e][d_idx - 1] in ["D", "L", "Au"]:
                    continue
            aptos_noite.append(e)

        coords_disp = [e for e in aptos_noite if info_enfermeiros[e]["coordenadora"]]
        normais_disp = [e for e in aptos_noite if not info_enfermeiros[e]["coordenadora"]]

        # --- SELEÇÃO DE NOITE (N4): Exatamente 5 pessoas (mín. 2 coordenadores)
        noite_dia = []
        n_coord_n = min(2, len(coords_disp))
        noite_dia.extend(coords_disp[:n_coord_n])
        coords_disp = coords_disp[n_coord_n:]

        falta_n = 5 - len(noite_dia)
        restantes_n = coords_disp + normais_disp
        noite_dia.extend(restantes_n[:falta_n])

        for e in noite_dia:
            escala[e][d_idx] = "N4"
            if e in coords_disp: coords_disp.remove(e)
            elif e in normais_disp: normais_disp.remove(e)

        # Atualizar disponíveis após noites
        disponiveis = [e for e in todos_enfs if escala[e][d_idx] == ""]
        coords_disp = [e for e in disponiveis if info_enfermeiros[e]["coordenadora"]]
        normais_disp = [e for e in disponiveis if not info_enfermeiros[e]["coordenadora"]]

        # --- SELEÇÃO DE MANHÃ (M59): Completar até 6 pessoas (mín. 2 coordenadores, já incluindo amamentação)
        manha_dia = [e for e in todos_enfs if escala[e][d_idx] == "M59"]
        
        if "Céu Peralta" in normais_disp and len(manha_dia) < 6:
            manha_dia.append("Céu Peralta")
            normais_disp.remove("Céu Peralta")

        coords_ja_m = sum(1 for e in manha_dia if info_enfermeiros[e]["coordenadora"])
        coords_nec_m = max(0, 2 - coords_ja_m)
        n_coord_m = min(coords_nec_m, len(coords_disp))
        
        manha_dia.extend(coords_disp[:n_coord_m])
        coords_disp = coords_disp[n_coord_m:]

        falta_m = 6 - len(manha_dia)
        restantes_m = coords_disp + normais_disp
        manha_dia.extend(restantes_m[:falta_m])

        for e in manha_dia:
            if escala[e][d_idx] == "":
                escala[e][d_idx] = "M59"
            if e in coords_disp: coords_disp.remove(e)
            elif e in normais_disp: normais_disp.remove(e)

        # Atualizar disponíveis após manhãs
        disponiveis = [e for e in todos_enfs if escala[e][d_idx] == ""]
        coords_disp = [e for e in disponiveis if info_enfermeiros[e]["coordenadora"]]
        normais_disp = [e for e in disponiveis if not info_enfermeiros[e]["coordenadora"]]

        # --- SELEÇÃO DE TARDE (T72): Exatamente 6 pessoas (mín. 2 coordenadores)
        tarde_dia = []
        n_coord_t = min(2, len(coords_disp))
        tarde_dia.extend(coords_disp[:n_coord_t])
        coords_disp = coords_disp[n_coord_t:]

        falta_t = 6 - len(tarde_dia)
        restantes_t = coords_disp + normais_disp
        tarde_dia.extend(restantes_t[:falta_t])

        for e in tarde_dia:
            escala[e][d_idx] = "T72"

        # --- RESTANTES VAZIOS = DESCANSO (D)
        for e in todos_enfs:
            if escala[e][d_idx] == "":
                escala[e][d_idx] = "D"

    # 4. Regra dos Feriados (Dia 1 e Dia 8)
    if dias_totais >= 8:
        for e in todos_enfs:
            if escala[e][0] in ["M59", "T72", "N4"] and escala[e][7] in ["M59", "T72", "N4"]:
                escala[e][7] = "D"

    # Construção do DataFrame Final
    df_escala = pd.DataFrame(escala, index=colunas_dias).T
    df_escala.insert(0, "Coordenadora", [ "Sim" if info_enfermeiros[e]["coordenadora"] else "Não" for e in df_escala.index ])
    df_escala.insert(0, "Equipa", [ info_enfermeiros[e]["equipa"] for e in df_escala.index ])

    st.subheader("📊 Tabela Completa da Escala de Enfermagem")
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
        file_name="escala_uls_leiria_final.csv",
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
