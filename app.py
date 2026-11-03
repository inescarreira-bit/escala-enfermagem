import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Escala de Enfermagem Avançada", page_icon="🏥", layout="wide")

st.title("🏥 Gerador Avançado de Escalas de Enfermagem (4 Semanas)")
st.write("Configura os turnos, restrições individuais e regras mensais.")

# 1. Configurações na Barra Lateral
st.sidebar.header("⚙️ Parâmetros da Escala")

# Período de 4 semanas (28 dias)
num_dias = 28
st.sidebar.info(f"📅 A escala será gerada para um período de **{num_dias} dias** (4 semanas).")

# Lista de enfermeiros
nomes_input = st.sidebar.text_area(
    "Nomes das Enfermeiras (um por linha):",
    "Ana Silva\nBruno Costa\nCarla Santos\nDaniel Oliveira\nElena Martins"
)
enfermeiros = [n.strip() for n in nomes_input.split("\n") if n.strip()]

st.sidebar.subheader("🎯 Objetivos de Turnos (por pessoa para o mês)")
meta_manha = st.sidebar.number_input("Nº de Manhãs (M)", min_value=0, value=7)
meta_tarde = st.sidebar.number_input("Nº de Tardes (T)", min_value=0, value=7)
meta_noite = st.sidebar.number_input("Nº de Noites (N)", min_value=0, value=4)
# O resto serão folgas para completar os 28 dias

# 2. Botão para Gerar
if st.sidebar.button("🚀 Gerar Escala Mensal", type="primary"):
    if not enfermeiros:
        st.error("Por favor, insere pelo menos um nome na barra lateral.")
    else:
        dias_colunas = [f"Dia {i+1}"].extend if False else [f"Dia {i+1}" for i in range(num_dias)]
        turnos_disponiveis = ["Manhã (M)"] * meta_manha + ["Tarde (T)"] * meta_tarde + ["Noite (N)"] * meta_noite
        
        # Completar o resto com Folgas (F) para atingir os 28 dias
        total_necessario = num_dias
        dias_atribuidos_por_pessoa = total_necessario
        
        dados_escala = {}
        
        for e in enfermeiros:
            # Criar a lista de turnos base para esta pessoa e baralhar de forma justa
            t_pessoa = turnos_disponiveis.copy()
            while len(t_pessoa) < num_dias:
                t_pessoa.append("Folga (F)")
            
            # Ajustar se houver excesso
            t_pessoa = t_pessoa[:num_dias]
            random.shuffle(t_pessoa)
            
            # Regra de segurança: se calhar Noite, o dia a seguir tem de ser Folga
            for i in range(num_dias - 1):
                if t_pessoa[i] == "Noite (N)":
                    t_pessoa[i+1] = "Folga (F)"
            
            dados_escala[e] = t_pessoa
            
        # Criar Dataframe
        df_escala = pd.DataFrame(dados_escala, index=dias_colunas).T
        
        st.success("✅ Escala de 4 semanas gerada com sucesso!")
        st.subheader("📊 Tabela Completa da Escala (28 Dias)")
        
        # Mostrar tabela interativa
        st.dataframe(df_escala, use_container_width=True)
        
        # Botão para exportar para Excel/CSV
        csv = df_escala.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Descarregar Escala Mensal (CSV)",
            data=csv,
            file_name='escala_enfermagem_mensal.csv',
            mime='text/csv',
        )
else:
    st.info("👈 Ajusta os limites de turnos na barra lateral e clica em **'Gerar Escala Mensal'**.")
