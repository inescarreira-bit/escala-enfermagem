import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala ULS Leiria - Enfermagem Avançada", page_icon="🏥", layout="wide")

st.title("🏥 Gestor Avançado de Escalas de Enfermagem")
st.write("Configuração flexível: Regimes especiais (Amamentação/Roulement), metas de turnos, bloqueios e equidade em fins de semana.")

# ----------------------------------------------------
# 1. LEGENDA DE TURNOS OFICIAIS
# ----------------------------------------------------
TURNOS_CONFIG = {
    "D": "Descanso / Folga",
    "L": "Férias",
    "T72": "Tarde (8h30)",
    "M59": "Manhã (08h00-16h30)",
    "N4": "Noite (00h00-08h30)",
    "MTA13": "Turno Específico (08h00-17h30)",
    "AM": "Amamentação (Horário Reduzido/Fixo)",
    "Au": "Ausência Genérica",
    "GvR": "Gravidez de Risco"
}

# ----------------------------------------------------
# 2. CONFIGURAÇÃO DE DATAS E CALENDÁRIO
# ----------------------------------------------------
st.sidebar.header("📅 1. Período da Escala")
data_inicio = st.sidebar.date_input("Data de Início", value=date(2026, 10, 26))
data_fim = st.sidebar.date_input("Data de Fim", value=date(2026, 11, 22))

dias_totais = (data_fim - data_inicio).days + 1

if dias_totais <= 0:
    st.error("A data de fim tem de ser posterior à data de início.")
    st.stop()

dias_semana_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
colunas_dias = []
dias_fim_semana = [] # Guarda índices ou nomes de dias que são Fim de Semana (Sáb/Dom)

for i in range(dias_totais):
    dia_c = data_inicio + timedelta(days=i)
    nome_dia = f"{dia_c.strftime('%d/%m')} ({dias_semana_pt[dia_c.weekday()].lower()})"
    colunas_dias.append(nome_dia)
    if dia_c.weekday() in [5, 6]: # 5 = Sábado, 6 = Domingo
        dias_fim_semana.append(nome_dia)

st.sidebar.header("👥 2. Lista da Equipa")
nomes_default = "TERESA PEREIRA\nANA CRISTINA COSTA\nPATRICIA ANUNCIACAO\nMARLENE DIAS\nMARTA BRIGIDO"
nomes_input = st.sidebar.text_area("Enfermeiros (um por linha):", nomes_default, height=120)
enfermeiros = [n.strip() for n in nomes_input.split("\n") if n.strip()]

# ----------------------------------------------------
# 3. PERFIL E REGIME DE CADA ENFERMEIRO
# ----------------------------------------------------
st.subheader("⚙️ 1. Configuração Individual de Regimes e Metas de Turnos")
st.caption("Define a escala base (Roulement vs. Amamentação/Horário Fixo) e a meta de turnos para cada pessoa.")

if "perfis" not in st.session_state:
    st.session_state["perfis"] = {}

for e in enfermeiros:
    if e not in st.session_state["perfis"]:
        st.session_state["perfis"][e] = {
            "regime": "Roulement Completo",
            "meta_turnos": 18,
            "turno_preferencial": "M59"
        }

with st.expander("📝 Editar Perfil/Regime de cada Enfermeiro/a", expanded=True):
    for e in enfermeiros:
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            st.markdown(f"**{e}**")
        with c2:
            st.session_state["perfis"][e]["regime"] = st.selectbox(
                f"Regime ({e}):",
                ["Roulement Completo", "Amamentação / Horário Fixo", "Apenas Manhãs", "Apenas Tardes"],
                key=f"reg_{e}"
            )
        with c3:
            st.session_state["perfis"][e]["meta_turnos"] = st.number_input(
                f"Meta de Turnos de Trabalho ({e}):",
                min_value=0, max_value=dias_totais, value=st.session_state["perfis"][e]["meta_turnos"],
                key=f"meta_{e}"
            )

# ----------------------------------------------------
# 4. RESTRIÇÕES DE DIAS ESPECÍFICOS E BLOQUEIOS
# ----------------------------------------------------
st.divider()
st.subheader("📌 2. Bloqueio de Dias Específicos e Pedidos")
st.markdown("Mesmo que esteja em Roulement ou Amamentação, podes fixar dias em que a pessoa **não pode trabalhar** (ex: Folga/Descanso `D`, Férias `L`, etc.).")

if "bloqueios" not in st.session_state:
    st.session_state["bloqueios"] = {}

cb1, cb2, cb3 = st.columns(3)
with cb1:
    enf_sel = st.selectbox("Enfermeiro/a:", enfermeiros)
with cb2:
    dia_sel = st.selectbox("Dia do Calendário:", colunas_dias)
with cb3:
    estado_sel = st.selectbox("Turno/Estado Fixo:", ["D (Descanso/Folga)", "L (Férias)", "M59 (Manhã)", "T72 (Tarde)", "N4 (Noite)", "Au (Ausência)"])

sigla_estado = estado_sel.split
