import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala de Enfermagem Personalizada", page_icon="🏥", layout="wide")

st.title("🏥 Gerador de Escalas de Enfermagem (Calendário Real)")
st.write("Cria a escala para 4 semanas com datas reais, dias da semana e controlo de turnos.")

# 1. Configurações na Barra Lateral
st.sidebar.header("📅 1. Selecionar Calendário")
data_inicio = st.sidebar.date_input("Data de Início (Dia 1 da Escala)", value=date.today())
num_dias = 28  # Período de 4 semanas

# Gerar automaticamente os dias e nomes dos dias da semana em português
dias_semana_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
colunas_dias = []

for i in range(num_dias):
    dia_atual = data_inicio + timedelta(days=i)
    nome_dia_sem = dias_semana_pt[dia_atual.weekday()]
    # Formato exato: "01/11 (Seg)"
    colunas_dias.append(f"{dia_atual.strftime('%d/%m')} ({nome_dia_sem})")

st.sidebar.header("👥 2. Enfermeiras e Turnos")
nomes_input = st.sidebar.text_area(
    "Nomes das Enfermeiras (um por linha):",
    "Ana Silva\nBruno Costa\nCarla Santos\nDaniel Oliveira\nElena Martins"
)
enfermeiros = [n.strip() for n in nomes_input.split("\n") if n.strip()]

st.sidebar.subheader("⚙️ Metas Mensais por Pessoa")
meta_manha = st.sidebar.number_input("Nº de Manhãs (M)", min_value=0, value=7)
meta_tarde = st.sidebar.number_input("Nº de Tardes (T)", min_value=0, value=7)
meta_noite = st.sidebar.number_input("Nº de Noites (N)", min_value=0, value=4)
# O restante dos 28 dias é preenchido automaticamente com Folgas (F)

# 2. Botão Principal para Gerar
if st.sidebar.button("🚀 Gerar Escala Mensal com Datas", type="primary"):
    if not enfermeiros:
        st.error("Por favor, insere pelo menos um nome na barra lateral.")
    else:
        turnos_base = ["Manhã (M)"] * meta_manha + ["Tarde (T)"] * meta_tarde + ["Noite (N)"] * meta_noite
        
        dados_escala = {}
        
        for e in enfermeiros:
            t_pessoa = turnos_base.copy()
            # Completar os dias restantes do mês com Folgas
            while len(t_pessoa) < num_dias:
                t_pessoa.append("Folga (F)")
            
            t_pessoa = t_pessoa[:num_dias]
            random.shuffle(t_pessoa)
            
            # Regra de segurança: se calhar Noite, o dia seguinte tem de ser obrigatoriamente Folga
            for i in range(num_dias - 1):
                if t_pessoa[i] == "Noite (N)":
                    t_pessoa[i+1] = "Folga (F)"
            
            dados_escala[e] = t_pessoa
            
        # Criar a tabela associando as linhas aos enfermeiros e as colunas às datas reais
        df_escala = pd.DataFrame(dados_escala, index=colunas_dias).T
        
        st.success("✅ Escala de 4 semanas gerada com sucesso com base no calendário real!")
        st.subheader("📊 Tabela Completa (4 Semanas / 28 Dias)")
        
        # Mostrar tabela interativa ajustada ao ecrã largo
        st.dataframe(df_escala, use_container_width=True)
        
        # Botão para descarregar o ficheiro Excel/CSV
        csv = df_escala.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Descarregar Escala Mensal (CSV/Excel)",
            data=csv,
            file_name=f'escala_enfermagem_{data_inicio.strftime("%Y-%m-%d")}.csv',
            mime='text/csv',
        )
else:
    st.info("👈 Escolhe a data de início no calendário à esquerda, ajusta os turnos e clica em **'Gerar Escala Mensal com Datas'**.")
