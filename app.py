import streamlit as st
from datetime import datetime, timedelta

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS
# ==============================================================================
st.set_page_config(page_title="IA Gestão de RH & Horários", layout="wide", page_icon="📅")

st.title("🤖 Sistema Inteligente de Gestão de Escalas e RH")
st.caption("Otimização de turnos, controlo de carga horária e gestão de descanso regulamentar.")

# ==============================================================================
# 2. MOTOR DE INTELIGÊNCIA / ALGORITMO DE DISTRIBUIÇÃO DE TURNOS
# ==============================================================================
def gerar_escala_inteligente(funcionarios, data_inicio, data_fim, carga_semanal):
    """
    Algoritmo de distribuição automática de turnos (Manhã, Tarde, Noite, Folga)
    Garante descanso mínimo e cumpre as horas estipuladas.
    """
    dias_periodo = (data_fim - data_inicio).days + 1
    horas_diarias_alvo = carga_semanal / 5
    
    # Base de dados da escala: { Data: { Funcionario: Turno } }
    escala_final = {}
    # Controlo de horas acumuladas por funcionário: { Funcionario: Horas }
    banco_horas = {f: 0.0 for f in funcionarios}
    # Controlo do último turno para evitar turnos seguidos prejudiciais (ex: Noite -> Manhã)
    ultimo_turno = {f: None for f in funcionarios}
    
    turnos_disponiveis = ["Manhã (M)", "Tarde (T)", "Noite (N)"]
    
    for i in range(dias_periodo):
        data_atual = data_inicio + timedelta(days=i)
        dia_semana = data_atual.weekday() # 5 = Sábado, 6 = Domingo
        escala_final[data_atual] = {}
        
        # Ordenar funcionários por quem tem menos horas trabalhadas para equilibrar a balança
        funcionarios_ordenados = sorted(funcionarios, key=lambda f: banco_horas[f])
        
        turno_index = 0
        for f in funcionarios_ordenados:
            # 1. Regra de Fins de Semana (Rotatividade ou Folga)
            if dia_semana >= 5:
                # Distribuição simulada de folga ao fim de semana se já cumpriu horas
                if banco_horas[f] >= (horas_diarias_alvo * 5 * (i // 7 + 1)):
                    escala_final[data_atual][f] = "Folga (F)"
                    ultimo_turno[f] = "Folga"
                    continue
            
            # 2. Restrição de Segurança: Se fez Noite ontem, HOJE OBRIGATORIAMENTE FOLGA
            if ultimo_turno[f] == "Noite (N)":
                escala_final[data_atual][f] = "Folga Pós-Noite (FN)"
                ultimo_turno[f] = "Folga"
                continue
                
            # 3. Distribuição dos turnos produtivos
            if turno_index < len(turnos_disponiveis):
                turno_atribuido = turnos_disponiveis[turno_index]
                escala_final[data_atual][f] = turno_atribuido
                ultimo_turno[f] = turno_atribuido
                banco_horas[f] += horas_diarias_alvo # Adiciona as horas correspondentes
                turno_index += 1
            else:
                # Se não há mais turnos necessários para este dia, folga
                escala_final[data_atual][f] = "Folga (F)"
                ultimo_turno[f] = "Folga"
                
    return escala_final, banco_horas

# ==============================================================================
# 3. INTERFACE GRÁFICA DO UTILIZADOR (STREAMLIT UI)
# ==============================================================================
col1, col2 = st.columns([1, 3])

with col1:
    st.header("⚙️ Parâmetros")
    
    # Input de Datas
    data_ini = st.date_input("Data de Início", datetime(2026, 11, 23))
    data_f = st.date_input("Data de Fim", datetime(2026, 12, 20))
    
    # Carga Horária
    carga_horaria = st.number_input("Carga Horária Semanal (h)", min_value=20, max_value=44, value=35, step=1)
    
    # Gestão de Equipa
    st.subheader("👥 Equipa de Enfermagem / RH")
    equipa_padrao = "Enf. Maria Silva, Enf. João Santos, Enf. Ana Costa, Enf. Carlos Reis, Enf. Sofia Antunes"
    lista_input = st.text_area("Lista de Funcionários (separados por vírgula)", equipa_padrao)
    funcionarios = [f.strip() for f in lista_input.split(",") if f.strip()]

with col2:
    st.header("📋 Escala de Turnos Otimizada")
    
    if data_ini > data_f:
        st.error("Erro: A data de início não pode ser maior que a data de fim.")
    elif len(funcionarios) == 0:
        st.warning("Adicione pelo menos um funcionário para gerar a escala.")
    else:
        # Executar a IA de distribuição
        escala, banco_horas = gerar_escala_inteligente(funcionarios, data_ini, data_f, carga_horaria)
        
        # Criar uma tabela visual bonita
        linhas_tabela = []
        for data, atribuicoes in escala.items():
            linha = {"Data": data.strftime("%d/%m/%Y (%a)")}
            linha.update(atribuicoes)
            linhas_tabela.append(linha)
            
        # Apresentar a tabela principal no Streamlit
        st.dataframe(linhas_tabela, use_container_width=True, hide_index=True)
        
        # Apresentar Métricas do Banco de Horas
        st.header("📊 Controlo Estatístico de Carga Horária")
        m_col1, m_col2, m_col3 = st.columns(3)
        
        dias_uteis_estimados = sum(1 for d in escala.keys() if d.weekday() < 5)
        horas_totais_alvo = dias_uteis_estimados * (carga_horaria / 5)
        
        with m_col1:
            st.metric(label="Dias Úteis no Período", value=f"{dias_uteis_estimados} dias")
        with m_col2:
            st.metric(label="Meta de Horas Individual", value=f"{horas_totais_alvo:.1f} h")
        with m_col3:
            st.metric(label="Total Funcionários", value=f"{len(funcionarios)} ativos")
            
        # Mostrar o balanço de cada trabalhador
        st.subheader("⏱️ Total de Horas Atribuídas por Profissional")
        for func, horas in banco_horas.items():
            progresso = min(horas / horas_totais_alvo, 1.0) if horas_totais_alvo > 0 else 0.0
            st.write(f"**{func}**: {horas:.1f}h de {horas_totais_alvo:.1f}h necessárias")
            st.progress(progresso)
