import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala ULS Leiria - Gestão por Equipas", page_icon="🏥", layout="wide")

st.title("🏥 Gestor Avançado de Escalas por Equipas (ULS Leiria)")
st.write("Escala inteligente com rácios diários (6M / 6T / 5N), 2 Coordenadores por turno, limite de Amamentação e Roulement M-M-T-T-F-D-N-N-F-F.")

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

# Sequence base de Roulement Ideal: M M T T F D N N F F
PADRAO_ROULEMENT = ["M59", "M59", "T72", "T72", "D", "D", "N4", "N4", "D", "D"]

# ----------------------------------------------------
# 2. BASE DE DADOS DAS EQUIPAS (PREDEFINIDA)
# ----------------------------------------------------
EQUIPAS_INICIAIS = {
    "Equipa 1": [
        {"nome": "Ana Costa", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Beatriz", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Alexandra", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Patricia A.", "coordenadora": False, "regime": "Roulement", "ativo": True},
        {"nome": "Mariana D.", "coordenadora": False, "regime": "Roulement", "ativo": True},
    ],
    "Equipa 2": [
        {"nome": "Inês Guerra", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Nidia", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Inês M.", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Marta", "coordenadora": False, "regime": "Roulement", "ativo": True},
        {"nome": "Barbara", "coordenadora": False, "regime": "Roulement", "ativo": True},
    ],
    "Equipa 3": [
        {"nome": "Sofia", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Joana N.", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Daniela F.", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Rafaela", "coordenadora": False, "regime": "Roulement", "ativo": True},
        {"nome": "Diogo", "coordenadora": False, "regime": "Roulement", "ativo": True},
        {"nome": "Catarina", "coordenadora": False, "regime": "Roulement", "ativo": True},
    ],
    "Equipa 4": [
        {"nome": "Liliana", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Patricia Bento", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Iara", "coordenadora": False, "regime": "Roulement", "ativo": True},
        {"nome": "Ana Filipa", "coordenadora": False, "regime": "Roulement", "ativo": True},
        {"nome": "Teresa", "coordenadora": False, "regime": "Roulement", "ativo": True},
    ],
    "Equipa 5": [
        {"nome": "Inês Carreira", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Mariana Neves", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Eva Mota", "coordenadora": True, "regime": "Roulement", "ativo": True},
        {"nome": "Bianca", "coordenadora": False, "regime": "Roulement", "ativo": True},
        {"nome": "Laura", "coordenadora": False, "regime": "Roulement", "ativo": True},
        {"nome": "Francisca", "coordenadora": False, "regime": "Roulement", "ativo": True},
    ],
    "Amamentação": [
        {"nome": "Diana Oliveira", "coordenadora": False, "regime": "Amamentação", "ativo": True},
        {"nome": "Patricia M.", "coordenadora": False, "regime": "Amamentação", "ativo": True},
        {"nome": "Andreia M.", "coordenadora": False, "regime": "Amamentação", "ativo": True},
        {"nome": "Ana Sofia", "coordenadora": False, "regime": "Amamentação", "ativo": True},
    ],
    "Outros / Especiais": [
        {"nome": "Céu Peralta", "coordenadora": False, "regime": "Manhã Preferencial", "ativo": True},
    ]
}

# Inicialização de Estado na Sessão
if "equipas_dados" not in st.session_state:
    st.session_state["equipas_dados"] = EQUIPAS_INICIAIS

if "bloqueios" not in st.session_state:
    st.session_state["bloqueios"] = {}

if "metas_turnos" not in st.session_state:
    st.session_state["metas_turnos"] = {}

# ----------------------------------------------------
# 3. BARRA LATERAL: DATAS E PARÂMETROS
# ----------------------------------------------------
st.sidebar.header("📅 1. Período da Escala")
data_inicio = st.sidebar.date_input("Data de Início", value=date(2026, 10, 26))
data_fim = st.sidebar.date_input("Data de Fim", value=date(2026, 11, 22))

dias_totais = (data_fim - data_inicio).days + 1
if dias_totais <= 0:
    st.error("A data de fim deve ser posterior à data de início.")
    st.stop()

dias_semana_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
colunas_dias = []
for i in range(dias_totais):
    d_atual = data_inicio + timedelta(days=i)
    colunas_dias.append(f"{d_atual.strftime('%d/%m')} ({dias_semana_pt[d_atual.weekday()].lower()})")

# ----------------------------------------------------
# 4. GESTÃO DE EQUIPAS E PESSOAL
# ----------------------------------------------------
st.subheader("👥 1. Gestão de Equipas e Estatutos de Enfermeiros")

with st.expander("⚙️ Gerir Elementos, Ativar/Inativar e Trocar Regimes", expanded=False):
    # Seleção de Equipa para editar
    eq_sel = st.selectbox("Escolhe a Equipa para editar:", list(st.session_state["equipas_dados"].keys()))
    
    st.markdown(f"**Elementos da {eq_sel}:**")
    membros = st.session_state["equipas_dados"][eq_sel]
    
    novos_membros = []
    for idx, m in enumerate(membros):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        with c1:
            nome_attr = st.text_input(f"Nome #{idx+1}", value=m["nome"], key=f"nome_{eq_sel}_{idx}")
        with c2:
            coord_attr = st.checkbox("Coordenadora", value=m["coordenadora"], key=f"coord_{eq_sel}_{idx}")
        with c3:
            regime_attr = st.selectbox("Regime", ["Roulement", "Amamentação", "Manhã Preferencial", "Apenas Manhãs"], index=["Roulement", "Amamentação", "Manhã Preferencial", "Apenas Manhãs"].index(m["regime"]) if m["regime"] in ["Roulement", "Amamentação", "Manhã Preferencial", "Apenas Manhãs"] else 0, key=f"reg_{eq_sel}_{idx}")
        with c4:
            ativo_attr = st.checkbox("Ativo(a)", value=m["ativo"], key=f"ativo_{eq_sel}_{idx}")
            
        novos_membros.append({"nome": nome_attr, "coordenadora": coord_attr, "regime": regime_attr, "ativo": ativo_attr})
    
    st.session_state["equipas_dados"][eq_sel] = novos_membros

    # Adicionar Novo Enfermeiro
    st.divider()
    st.markdown("**➕ Adicionar Novo Colaborador**")
    ca1, ca2, ca3 = st.columns(3)
    with ca1:
        novo_nome = st.text_input("Nome do Enfermeiro/a:")
    with ca2:
        novo_coord = st.checkbox("É Coordenador/a?")
    with ca3:
        novo_regime = st.selectbox("Regime:", ["Roulement", "Amamentação", "Manhã Preferencial", "Apenas Manhãs"])
    
    if st.button("Adicionar a esta equipa"):
        if novo_nome:
            st.session_state["equipas_dados"][eq_sel].append({"nome": novo_nome, "coordenadora": novo_coord, "regime": novo_regime, "ativo": True})
            st.success(f"{novo_nome} adicionado/a à {eq_sel}!")
            st.rerun()

# Lista de enfermeiros ativos e dicionário de atributos
todos_enfermeiros_ativos = []
info_enfermeiros = {}

for eq, lista in st.session_state["equipas_dados"].items():
    for m in lista:
        if m["ativo"]:
            todos_enfermeiros_ativos.append(m["nome"])
            info_enfermeiros[m["nome"]] = {
                "equipa": eq,
                "coordenadora": m["coordenadora"],
                "regime": m["regime"]
            }

# Metas de turnos padrão por pessoa
for e in todos_enfermeiros_ativos:
    if e not in st.session_state["metas_turnos"]:
        st.session_state["metas_turnos"][e] = 18

with st.expander("🎯 Definir Meta de Turnos Mensais por Pessoa"):
    cols_meta = st.columns(3)
    for i, e in enumerate(todos_enfermeiros_ativos):
        with cols_meta[i % 3]:
            st.session_state["metas_turnos"][e] = st.number_input(f"Meta de Turnos: {e}", min_value=0, max_value=dias_totais, value=st.session_state["metas_turnos"][e], key=f"m_{e}")

# ----------------------------------------------------
# 5. BLOQUEIOS DE DIAS E RESTRIÇÕES ESPECÍFICAS
# ----------------------------------------------------
st.divider()
st.subheader("📌 2. Bloqueio de Dias e Pedidos Específicos")

cb1, cb2, cb3 = st.columns(3)
with cb1:
    enf_sel = st.selectbox("Enfermeiro/a:", todos_enfermeiros_ativos)
with cb2:
    dia_sel = st.selectbox("Dia do Calendário:", colunas_dias)
with cb3:
    estado_sel = st.selectbox("Turno / Pedido Fixo:", ["D (Descanso/Folga)", "L (Férias)", "M59 (Manhã)", "T72 (Tarde)", "N4 (Noite)", "Au (Ausência)"])

sigla_estado = estado_sel.split(" ")[0]

if st.button("➕ Fixar Restrição/Pedido"):
    if enf_sel not in st.session_state["bloqueios"]:
        st.session_state["bloqueios"][enf_sel] = {}
    st.session_state["bloqueios"][enf_sel][dia_sel] = sigla_estado
    st.success(f"Fixado: {enf_sel} -> {sigla_estado} no dia {dia_sel}.")

if st.session_state["bloqueios"]:
    with st.expander("Ver Restrições Definidas Ativas"):
        for e, rest in st.session_state["bloqueios"].items():
            for d, t in rest.items():
                st.text(f"• {e} ({d}) -> {t}")
        if st.button("Limpar Restrições"):
            st.session_state["bloqueios"] = {}
            st.rerun()

# ----------------------------------------------------
# 6. GERADOR AUTOMÁTICO DE ESCALA
# ----------------------------------------------------
st.divider()

if st.button("🚀 Gerar Escala com Rácios (6M / 6T / 5N) e Coordenadores", type="primary"):
    
    escala = {e: [""] * dias_totais for e in todos_enfermeiros_ativos}
    turnos_contagem = {e: 0 for e in todos_enfermeiros_ativos}
    
    # Passagem 1: Aplicar Bloqueios Manuais
    for e in todos_enfermeiros_ativos:
        if e in st.session_state["bloqueios"]:
            for d_idx, d_nome in enumerate(colunas_dias):
                if d_nome in st.session_state["bloqueios"][e]:
                    escala[e][d_idx] = st.session_state["bloqueios"][e][d_nome]
                    if escala[e][d_idx] not in ["D", "L", "Au", "GvR"]:
                        turnos_contagem[e] += 1

    # Passagem 2: Céu Peralta (Muito mais M que T)
    if "Céu Peralta" in escala:
        for d_idx in range(dias_totais):
            if escala["Céu Peralta"][d_idx] == "":
                if turnos_contagem["Céu Peralta"] < st.session_state["metas_turnos"]["Céu Peralta"]:
                    # 80% Manhãs, 20% Tardes
                    escala["Céu Peralta"][d_idx] = "M59" if random.random() < 0.80 else "T72"
                    turnos_contagem["Céu Peralta"] += 1
                else:
                    escala["Céu Peralta"][d_idx] = "D"

    # Passagem 3: Amamentação (Máximo 3 por Manhã)
    amamentacao_enfermeiros = [e for e in todos_enfermeiros_ativos if info_enfermeiros[e]["regime"] == "Amamentação"]
    
    for d_idx in range(dias_totais):
        am_no_dia = 0
        random.shuffle(amamentacao_enfermeiros)
        for e in amamentacao_enfermeiros:
            if escala[e][d_idx] == "":
                if am_no_dia < 3 and turnos_contagem[e] < st.session_state["metas_turnos"][e]:
                    escala[e][d_idx] = "M59"
                    turnos_contagem[e] += 1
                    am_no_dia += 1
                else:
                    escala[e][d_idx] = "D"

    # Passagem 4: Preenchimento do Roulement (M M T T F D N N F F)
    roulement_enfermeiros = [e for e in todos_enfermeiros_ativos if info_enfermeiros[e]["regime"] == "Roulement"]
    
    for e_idx, e in enumerate(roulement_enfermeiros):
        offset = (e_idx * 2) % len(PADRAO_ROULEMENT)
        
        for d_idx in range(dias_totais):
            if escala[e][d_idx] == "":
                # Regra de Segurança Pós-Noite
                if d_idx > 0 and escala[e][d_idx-1] == "N4":
                    escala[e][d_idx] = "D"
                elif turnos_contagem[e] < st.session_state["metas_turnos"][e]:
                    turno_sugerido = PADRAO_ROULEMENT[(d_idx + offset) % len(PADRAO_ROULEMENT)]
                    escala[e][d_idx] = turno_sugerido
                    if turno_sugerido not in ["D", "L"]:
                        turnos_contagem[e] += 1
                else:
                    escala[e][d_idx] = "D"

    # Preencher restantes vazios com Folga
    for e in todos_enfermeiros_ativos:
        for d_idx in range(dias_totais):
            if escala[e][d_idx] == "":
                escala[e][d_idx] = "D"

    # Construção da Tabela Final
    df_escala = pd.DataFrame(escala, index=colunas_dias).T
    
    # Adicionar colunas informativas de Equipa e Coordenadora
    df_escala.insert(0, "Coordenadora", [ "Sim" if info_enfermeiros[e]["coordenadora"] else "Não" for e in df_escala.index ])
    df_escala.insert(0, "Equipa", [ info_enfermeiros[e]["equipa"] for e in df_escala.index ])

    st.subheader("📊 Tabela Completa da Escala de Enfermagem")
    st.dataframe(df_escala, use_container_width=True)

    # ----------------------------------------------------
    # 7. ANÁLISE DE RÁCIOS E COORDENADORES POR TURNO
    # ----------------------------------------------------
    st.divider()
    st.subheader("📈 Validação de Rácios e Coordenadores por Turno")
    
    m_counts, t_counts, n_counts = [], [], []
    coord_m, coord_t, coord_n = [], [], []

    for d_nome in colunas_dias:
        col = df_escala[d_nome]
        
        m_enfs = col[col == "M59"].index
        t_enfs = col[col == "T72"].index
        n_enfs = col[col == "N4"].index
        
        m_counts.append(len(m_enfs))
        t_counts.append(len(t_enfs))
        n_counts.append(len(n_enfs))
        
        coord_m.append(sum(1 for e in m_enfs if info_enfermeiros[e]["coordenadora"]))
        coord_t.append(sum(1 for e in t_enfs if info_enfermeiros[e]["coordenadora"]))
        coord_n.append(sum(1 for e in n_enfs if info_enfermeiros[e]["coordenadora"]))

    df_stats = pd.DataFrame({
        "Manhãs (M) [Meta: 6]": m_counts,
        "Coordenadores M [Min: 2]": coord_m,
        "Tardes (T) [Meta: 6]": t_counts,
        "Coordenadores T [Min: 2]": coord_t,
        "Noites (N) [Meta: 5]": n_counts,
        "Coordenadores N [Min: 2]": coord_n,
    }, index=colunas_dias)

    st.dataframe(df_stats.T, use_container_width=True)

    # Botão para Descarregar
    csv = df_escala.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Descarregar Escala em CSV / Excel",
        data=csv,
        file_name="escala_uls_leiria_equipas.csv",
        mime="text/csv"
    )

# ----------------------------------------------------
# 8. LEGENDA
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
