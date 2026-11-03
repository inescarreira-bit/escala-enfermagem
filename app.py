import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala ULS Leiria - Enfermagem", page_icon="🏥", layout="wide")

st.title("🏥 Gestor de Escalas de Enfermagem - Com Bloqueios Individuais")
st.write("Sistema de gestão de horários com códigos oficiais e restrições por dia/enfermeiro.")

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
    "Au": "Ausência Genérica",
    "GvR": "Gravidez de Risco"
}

# ----------------------------------------------------
# 2. CONFIGURAÇÕES NA BARRA LATERAL
# ----------------------------------------------------
st.sidebar.header("📅 Período da Escala")
data_inicio = st.sidebar.date_input("Data de Início", value=date(2026, 10, 26))
data_fim = st.sidebar.date_input("Data de Fim", value=date(2026, 11, 22))

dias_totais = (data_fim - data_inicio).days + 1

if dias_totais <= 0:
    st.error("A data de fim tem de ser posterior à data de início.")
    st.stop()

dias_semana_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
colunas_dias = []
for i in range(dias_totais):
    dia_c = data_inicio + timedelta(days=i)
    colunas_dias.append(f"{dia_c.strftime('%d/%m')} ({dias_semana_pt[dia_c.weekday()].lower()})")

st.sidebar.header("👥 Lista da Equipa")
nomes_default = "TERESA PEREIRA\nANA CRISTINA COSTA\nPATRICIA ANUNCIACAO\nMARLENE DIAS\nMARTA BRIGIDO"
nomes_input = st.sidebar.text_area("Enfermeiros (um por linha):", nomes_default, height=150)
enfermeiros = [n.strip() for n in nomes_input.split("\n") if n.strip()]

# ----------------------------------------------------
# 3. GESTÃO DE BLOQUEIOS E RESTRIÇÕES POR PESSOA
# ----------------------------------------------------
st.subheader("⚙️ Atribuir Indisponibilidades ou Pedidos Específicos")
st.markdown("Aqui podes definir se um determinado enfermeiro **não pode trabalhar num dia específico** (ex: fica de folga/descanso `D` ou ausente) antes de gerar a escala.")

if "bloqueios" not in st.session_state:
    st.session_state["bloqueios"] = {} # Formato: {enfermeiro: {dia: turno_fixo}}

col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    enf_selecionado = st.selectbox("1. Selecionar Enfermeiro/a:", enfermeiros)
with col_b2:
    dia_bloqueio = st.selectbox("2. Selecionar o Dia:", colunas_dias)
with col_b3:
    turno_atribuido = st.selectbox("3. O que acontece neste dia?", ["D (Descanso/Folga Obrigatória)", "L (Férias)", "Au (Ausência)", "GvR (Gravidez de Risco)"])

# Extrair apenas a sigla inicial (ex: "D" de "D (Descanso...)")
sigla_turno = turno_atribuido.split(" ")[0]

if st.button("➕ Adicionar Indisponibilidade/Restrição"):
    if enf_selecionado not in st.session_state["bloqueios"]:
        st.session_state["bloqueios"][enf_selecionado] = {}
    
    st.session_state["bloqueios"][enf_selecionado][dia_bloqueio] = sigla_turno
    st.success(f"Registado: **{enf_selecionado}** fica com **{sigla_turno}** no dia **{dia_bloqueio}**.")

# Mostrar lista de bloqueios ativos atuais
if st.session_state["bloqueios"]:
    with st.expander("📌 Ver Restrições e Bloqueios Atualmente Definidos"):
        for e, restricoes in st.session_state["bloqueios"].items():
            for d, t in restricoes.items():
                st.text(f"• {e} -> No dia {d} tem fixado o estado: {t}")
        if st.button("🗑️ Limpar Todos os Bloqueios"):
            st.session_state["bloqueios"] = {}
            st.rerun()

# ----------------------------------------------------
# 4. GERADOR DA ESCALA AUTOMÁTICA RESPEITANDO OS BLOQUEIOS
# ----------------------------------------------------
st.divider()

if st.button("🚀 Gerar Escala Final Respeitando Restrições", type="primary"):
    dados_escala = {}
    turnos_sorteio = ["M59", "T72", "N4", "D", "D"]
    
    for e in enfermeiros:
        escala_pessoa = []
        ultimo_turno = ""
        
        for dia in colunas_dias:
            # 1. Verificar se existe um bloqueio/restrição manual para esta pessoa neste dia exato
            if e in st.session_state["bloqueios"] and dia in st.session_state["bloqueios"][e]:
                t = st.session_state["bloqueios"][e][dia]
            else:
                # 2. Regra de segurança hospitalar: após um turno de Noite (N4), o dia seguinte é obrigatoriamente Descanso (D)
                if ultimo_turno == "N4":
                    t = "D"
                else:
                    t = random.choice(turnos_sorteio)
            
            escala_pessoa.append(t)
            ultimo_turno = t
            
        dados_escala[e] = escala_pessoa

    df = pd.DataFrame(dados_escala, index=colunas_dias).T
    
    st.subheader("📊 Tabela de Horários Final")
    st.dataframe(df, use_container_width=True)
    
    # Botão de exportação
    csv = df.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Descarregar Escala em CSV / Excel",
        data=csv,
        file_name="escala_uls_com_restricoes.csv",
        mime="text/csv"
    )

# ----------------------------------------------------
# 5. LEGENDA NO RODAPÉ
# ----------------------------------------------------
st.divider()
st.subheader("📖 Legenda de Turnos")
col_l1, col_l2 = st.columns(2)
itens = list(TURNOS_CONFIG.items())
metade = len(itens) // 2

with col_l1:
    for k, v in itens[:metade]:
        st.write(f"**{k}**: {v}")
with col_l2:
    for k, v in itens[metade:]:
        st.write(f"**{k}**: {v}")
