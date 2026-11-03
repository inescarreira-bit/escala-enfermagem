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
    with ca
