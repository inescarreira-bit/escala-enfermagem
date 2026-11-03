import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala ULS Leiria - Rácios Garantidos", page_icon="🏥", layout="wide")

st.title("🏥 Gestor de Escalas de Enfermagem - ULS Leiria")
st.write("Garantia absoluta de rácios diários (6 Manhãs, 6 Tardes, 5 Noites) com no mínimo 2 coordenadores por turno, fins de semana alternados e proteção de descanso à segunda-feira.")

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

PADRAO_ROULEMENT = ["M59", "M59", "T72", "T72", "D", "D", "N4", "N4", "D", "D"]

# ----------------------------------------------------
# 2. BASE DE DADOS DAS EQUIPAS (Sessão Persistente)
# ----------------------------------------------------
EQUIPAS_INICIAIS = {
    "Equipa 1": [
        {"nome": "Ana Costa", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Beatriz", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Alexandra", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Patricia A.", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Mariana D.", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
    ],
    "Equipa 2": [
        {"nome": "Inês Guerra", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Nidia", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Inês M.", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Marta", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Barbara", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
    ],
    "Equipa 3": [
        {"nome": "Sofia", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Joana N.", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Daniela F.", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Rafaela", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Diogo", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Catarina", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
    ],
    "Equipa 4": [
        {"nome": "Liliana", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Patricia Bento", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Iara", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Ana Filipa", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Teresa", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
    ],
    "Equipa 5": [
        {"nome": "Inês Carreira", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Mariana Neves", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Eva Mota", "coordenadora": True, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Bianca", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Laura", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
        {"nome": "Francisca", "coordenadora": False, "ativo": True, "tipo_horario": "Roulement"},
    ],
    "Amamentação": [
        {"nome": "Diana Oliveira", "coordenadora": False, "ativo": True, "tipo_horario": "Fixo"},
        {"nome": "Patricia M.", "coordenadora": False, "ativo": True, "tipo_horario": "Fixo"},
        {"nome": "Andreia M.", "coordenadora": False, "ativo": True, "tipo_horario": "Fixo"},
        {"nome": "Ana Sofia", "coordenadora": False, "ativo": True, "tipo_horario": "Fixo"},
    ],
    "Outros / Especiais": [
        {"nome": "Céu Peralta", "coordenadora": False, "ativo": True, "tipo_horario": "Fixo"},
    ]
}

if "equipas_dados" not in st.session_state:
    st.session_state["equipas_dados"] = EQUIPAS_INICIAIS

if "escala_final" not in st.session_state:
    st.session_state["escala_final"] = None

# ----------------------------------------------------
# 3. BARRA LATERAL: DATAS (4 Semanas)
# ----------------------------------------------------
st.sidebar.header("📅 Período da Escala (4 Semanas)")
data_inicio = st.sidebar.date_input("Data de Início (Segunda-feira)", value=date(2026, 10, 26))
data_fim = st.sidebar.date_input("Data de Fim (Domingo)", value=date(2026, 11, 22))

dias_totais = (data_fim - data_inicio).days + 1
if dias_totais <= 0:
    st.error("A data de fim deve ser posterior à data de início.")
    st.stop()

dias_semana_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
colunas_dias = []
lista_datas = []

for i in range(dias_totais):
    d_atual = data_inicio + timedelta(days=i)
    colunas_dias.append(f"{d_atual.strftime('%d/%m')} ({dias_semana_pt[d_atual.weekday()].lower()})")
    lista_datas.append(d_atual)

# ----------------------------------------------------
# 4. GESTÃO DE EQUIPAS (A tua interface funcional original)
# ----------------------------------------------------
st.subheader("👥 1. Gestão de Equipas, Coordenadores e Tipo de Horário")

with st.expander("⚙️ Gerir Elementos, Ativação, Coordenação e Adicionar Pessoal", expanded=False):
    eq_sel = st.selectbox("Escolhe a Equipa para gerir:", list(st.session_state["equipas_dados"].keys()))
    membros = st.session_state["equipas_dados"][eq_sel]
    
    novos_membros = []
    for idx, m in enumerate(membros):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        with c1:
            n_val = st.text_input(f"Nome #{idx+1}", value=m["nome"], key=f"n_{eq_sel}_{idx}")
        with c2:
            c_val = st.checkbox("Coord.", value=m["coordenadora"], key=f"c_{eq_sel}_{idx}")
        with c3:
            idx_tipo = 0 if m.get("tipo_horario", "Roulement") == "Roulement" else 1
            t_val = st.selectbox("Tipo", ["Roulement", "Fixo"], index=idx_tipo, key=f"t_{eq_sel}_{idx}")
        with c4:
            a_val = st.checkbox("Ativo(a)", value=m["ativo"], key=f"a_{eq_sel}_{idx}")
        novos_membros.append({"nome": n_val, "coordenadora": c_val, "ativo": a_val, "tipo_horario": t_val})
    st.session_state["equipas_dados"][eq_sel] = novos_membros

    st.divider()
    st.markdown("**➕ Adicionar Novo/a Enfermeiro/a a esta Equipa**")
    ca1, ca2, ca3, ca4 = st.columns([3, 2, 2, 2])
    with ca1:
        novo_nome = st.text_input("Nome do Novo Elemento:")
    with ca2:
        novo_coord = st.checkbox("É Coordenador/a?", key="novo_coord_chk")
    with ca3:
        novo_tipo = st.selectbox("Tipo de Horário", ["Roulement", "Fixo"], key="novo_tipo_sel")
    with ca4:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_adicionar = st.button("Adicionar à Equipa")

    if btn_adicionar:
        if novo_nome.strip():
            st.session_state["equipas_dados"][eq_sel].append({"nome": novo_nome.strip(), "coordenadora": novo_coord, "ativo": True, "tipo_horario": novo_tipo})
            st.success(f"'{novo_nome.strip()}' adicionado/a com sucesso à **{eq_sel}**!")
            st.rerun()
        else:
            st.error("Por favor, introduz um nome válido.")

# Compilar lista unificada de elementos ativos para o motor
lista_enfermeiros_ativos = []
for eq, lista in st.session_state["equipas_dados"].items():
    for m in lista:
        if m["ativo"]:
            # Guardamos o nome da equipa original para manter a estrutura do roulement
            m_completo = m.copy()
            m_completo["equipa_origem"] = eq
            lista_enfermeiros_ativos.append(m_completo)

# ----------------------------------------------------
# 5. MOTOR DE ESCALA INTELIGENTE (As tuas regras de FDS)
# ----------------------------------------------------
st.subheader("⚡ 2. Processamento Automático de Turnos")

def gerar_escala_com_regras_fds():
    # Inicializar matriz vazia preenchida com Folga ("D")
    df = pd.DataFrame("D", index=[e["nome"] for e in lista_enfermeiros_ativos], columns=colunas_dias)
    
    # Mapeamento de desfasamentos das equipas para cruzar turnos
    offsets = {"Equipa 1": 0, "Equipa 2": 2, "Equipa 3": 4, "Equipa 4": 6, "Equipa 5": 8}
    
    # Dicionário para controlar o histórico de Fins de Semana trabalhados de cada enfermeiro
    # Estrutura: { nome_enfermeiro: [indice_dos_fins_de_semana_trabalhados] }
    historico_fds = {e["nome"]: [] for e in lista_enfermeiros_ativos}

    for d_idx, data in enumerate(lista_datas):
        dia_semana = data.weekday() # 0 = Segunda, 5 = Sábado, 6 = Domingo
        col_atual = colunas_dias[d_idx]
        
        # Identificador único de qual fim de semana do ciclo estamos (FDS 0, 1, 2, 3...)
        fds_id = d_idx // 7 

        for enf_idx, enf in enumerate(lista_enfermeiros_ativos):
            nome = enf["nome"]
            eq = enf["equipa_origem"]
            
            # --- REGRA FIXOS (Amamentação / Especiais) ---
            if enf["tipo_horario"] == "Fixo":
                if dia_semana in:
                    df.at[nome, col_atual] = "D"
                else:
                    df.at[nome, col_atual] = "AM" if eq == "Amamentação" else "MTA13"
                continue

            # --- REGRAS DE ROULEMENT E FINS DE SEMANA ---
            offset = offsets.get(eq, 0)
            ciclo_idx = (d_idx + offset + (enf_idx % 2 * 2)) % len(PADRAO_ROULEMENT)
