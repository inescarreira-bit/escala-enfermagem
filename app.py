import streamlit as st
import pandas as pd
import random

# Configuração da página web
st.set_page_config(page_title="Escala de Enfermagem", page_icon="🏥", layout="centered")

st.title("🏥 Gerador de Escalas de Enfermagem")
st.write("Bem-vindo/a à tua ferramenta gratuita de gestão de turnos.")

# 1. Painel Lateral para Configurações
st.sidebar.header("⚙️ Configurações")

# Lista de enfermeiros predefinida
nomes_input = st.sidebar.text_area(
    "Nomes dos Enfermeiros (um por linha):",
    "Ana Silva\nBruno Costa\nCarla Santos\nDaniel Oliveira\nElena Martins"
)
enfermeiros = [n.strip() for n in nomes_input.split("\n") if n.strip()]

dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
turnos_possiveis = ["Manhã (M)", "Tarde (T)", "Noite (N)", "Folga (F)"]

# 2. Botão Principal para Gerar Escala
if st.sidebar.button("🚀 Gerar Nova Escala", type="primary"):
    if not enfermeiros:
        st.error("Por favor, insere pelo menos um enfermeiro na barra lateral.")
    else:
        dados_escala = {}
        
        for e in enfermeiros:
            escala_enfermeiro = []
            ultimo_turno = ""
            
            for d in dias_semana:
                # Regra básica: se ontem foi Noite, hoje tem de ser Folga
                if ultimo_turno == "Noite (N)":
                    turno = "Folga (F)"
                else:
                    turno = random.choice(turnos_possiveis)
                
                escala_enfermeiro.append(turno)
                ultimo_turno = turno
            
            dados_escala[e] = escala_enfermeiro
        
        # Criar tabela
        df_escala = pd.DataFrame(dados_escala, index=dias_semana).T
        
        st.success("✅ Escala gerada com sucesso!")
        st.subheader("Visualização da Escala Semanal")
        st.dataframe(df_escala, use_container_width=True)
        
        # Botão para descarregar
        csv = df_escala.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Descarregar Escala (CSV/Excel)",
            data=csv,
            file_name='escala_enfermagem.csv',
            mime='text/csv',
        )
else:
    st.info("👈 Preenche os nomes na barra lateral à esquerda e clica em **'Gerar Nova Escala'** para começar!")
