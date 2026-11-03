import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala ULS Leiria - Rigor por Equipas", page_icon="🏥", layout="wide")

st.title("🏥 Gestor de Escalas de Enfermagem - Rigor e Equipas (ULS Leiria)")
st.write("Cumprimento estrito de rácios (6M / 6T / 5N), 2 Coordenadores/turno, Equipa Coesa, Fins de Semana Justos e Bloqueios.")

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
        {"nome": "Céu Peralta", "coordenadora": False, "ativo": True}, # Prefere Manhãs
    ]
}

if "equipas_dados" not in st.session_state:
    st.session_state["equipas_dados"] = EQUIPAS_INICIAIS

if "bloqueios" not in st.session_state:
    st.session_state["bloqueios"] = {}

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
indices_fins_de_semana = [] # Pares de (Sábado_idx, Domingo_idx)

# Mapear fins de semana completos do período
sabs_doms = []
for i in range(dias_totais):
    d_atual = data_inicio + timedelta(days=i)
    colunas_dias.append(f"{d_atual.strftime('%d/%m')} ({dias_semana_pt[d_atual.weekday()].lower()})")
    if d_atual.weekday() == 5: # Sábado
        if i + 1 < dias_totais:
            sabs_doms.append((i, i+1))

# ----------------------------------------------------
# 4. GESTÃO DE EQUIPAS E ESTATUTOS
# ----------------------------------------------------
st.subheader("👥 1. Gestão de Equipas, Ativos e Coordenadores")

with st.expander("⚙️ Gerir Elementos, Ativar/Inativar ou Adicionar", expanded=False):
    eq_sel = st.selectbox("Equipa:", list(st.session_state["equipas_dados"].keys()))
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

if st.session_state["bloqueios"]:
    with st.expander("Ver Restrições Ativas"):
        for e, r in st.session_state["bloqueios"].items():
            for d, t in r.items():
                st.text(f"• {e} ({d}) -> {t}")
        if st.button("Limpar Todas as Restrições"):
            st.session_state["bloqueios"] = {}
            st.rerun()

# ----------------------------------------------------
# 6. GERADOR INTELIGENTE RIGOROSO
# ----------------------------------------------------
st.divider()

if st.button("🚀 Gerar Escala com Rigor Absoluto de Rácios e Fins de Semana", type="primary"):
    
    escala = {e: [""] * dias_totais for e in todos_enfs}
    
    # 1. Aplicar Bloqueios Manuais e Férias
    for e in todos_enfs:
        if e in st.session_state["bloqueios"]:
            for d_idx, d_nome in enumerate(colunas_dias):
                if d_nome in st.session_state["bloqueios"][e]:
                    escala[e][d_idx] = st.session_state["bloqueios"][e][d_nome]

    # 2. Garantir 1 Fim de Semana Completo de Folga por Pessoa (distribuído de forma justa)
    # Atribuir fim de semana de folga a cada enfermeiro de forma rotativa nos sabs_doms disponíveis
    if sabs_doms:
        for idx_e, e in enumerate(todos_enfs):
            # Escolher um fim de semana de folga para este enfermeiro de forma equilibrada
            fds_escolhido = sabs_doms[idx_e % len(sabs_doms)]
            sab_idx, dom_idx = fds_escolhido
            if escala[e][sab_idx] == "":
                escala[e][sab_idx] = "D"
            if escala[e][dom_idx] == "":
                escala[e][dom_idx] = "D"

    # 3. Preenchimento Diário Rigoroso (Respeitando Rácios: 6M, 6T, 5N e Coordenadores >= 2)
    amamentacao_lista = [e for e in todos_enfs if info_enfermeiros[e]["equipa"] == "Amamentação"]
    ceu_peralta = ["Céu Peralta"] if "Céu Peralta" in todos_enfs else []
    equipa_normal = [e for e in todos_enfs if e not in amamentacao_lista and e not in céu_peralta]

    for d_idx in range(dias_totais):
        # Identificar quem já tem folga fixa ou férias neste dia
        folgados_hoje = [e for e in todos_enfs if escala[e][d_idx] in ["D", "L", "Au", "GvR"]]
        disponiveis = [e for e in todos_enfs if escala[e][d_idx] == ""]
        
        # Separar coordenadores disponíveis e não coordenadores
        coords_disp = [e for e in disponiveis if info_enfermeiros[e]["coordenadora"]]
        normais_disp = [e for e in disponiveis if not info_enfermeiros[e]["coordenadora"]]

        # ----------------- NOITE (N4): Exige 5 pessoas, mín. 2 coordenadores
        noite_atribuida = []
        # Selecionar coordenadores para a noite (mínimo 2)
        n_coords_noite = min(2, len(coords_disp))
        noite_atribuida.extend(coords_disp[:n_coords_noite])
        coords_disp = coords_disp[n_coords_noite:]
        
        # Completar noite até 5 com disponíveis
        falta_noite = 5 - len(noite_atribuida)
        tot_disp_restantes = coords_disp + normais_disp
        noite_atribuida.extend(tot_disp_restantes[:falta_noite])
        
        # Atualizar disponíveis
        for e in noite_atribuida:
            escala[e][d_idx] = "N4"
            if e in coords_disp: coords_disp.remove(e)
            elif e in normais_disp: normais_disp.remove(e)

        # Regra de segurança pós-noite: dia seguinte é obrigatoriamente Descanso (D)
        if d_idx + 1 < dias_totais:
            for e in noite_atribuida:
                if escala[e][d_idx + 1] == "":
                    escala[e][d_idx + 1] = "D"

        # Atualizar listas após noites
        disponiveis = [e for e in todos_enfs if escala[e][d_idx] == ""]
        coords_disp = [e for e in disponiveis if info_enfermeiros[e]["coordenadora"]]
        normais_disp = [e for e in disponiveis if not info_enfermeiros[e]["coordenadora"]]

        # ----------------- MANHÃ (M59): Exige 6 pessoas (máx. 3 de amamentação), mín. 2 coordenadores
        manha_atribuida = []
        
        # Alocar amamentação (máximo 3)
        am_disp = [e for e in amamentacao_lista if escala[e][d_idx] == ""]
        am_a_colocar = am_disp[:3]
        manha_atribuida.extend(am_a_colocar)
        
        # Céu Peralta prefere Manhã se estiver disponível
        if "Céu Peralta" in normais_disp and len(manha_atribuida) < 6:
            manha_atribuida.append("Céu Peralta")
            normais_disp.remove("Céu Peralta")

        # Garantir coordenadores na manhã (mínimo 2 no total do turno)
        coords_ja_na_manha = sum(1 for e in manha_atribuida if info_enfermeiros[e]["coordenadora"])
        coords_necessarias = max(0, 2 - coords_ja_na_manha)
        
        n_coords_m = min(coords_necessarias, len(coords_disp))
        manha_atribuida.extend(coords_disp[:n_coords_m])
        coords_disp = coords_disp[n_coords_m:]

        # Completar manhã até 6
        falta_manha = 6 - len(manha_atribuida)
        tot_m_restantes = coords_disp + normais_disp
        manha_atribuida.extend(tot_m_restantes[:falta_manha])

        for e in manha_atribuida:
            escala[e][d_idx] = "M59"
            if e in coords_disp: coords_disp.remove(e)
            elif e in normais_disp: normais_disp.remove(e)
            elif e in am_a_colocar: pass

        # Atualizar disponíveis
        disponiveis = [e for e in todos_enfs if escala[e][d_idx] == ""]
        coords_disp = [e for e in disponiveis if info_enfermeiros[e]["coordenadora"]]
        normais_disp = [e for e in disponiveis if not info_enfermeiros[e]["coordenadora"]]

        # ----------------- TARDE (T72): Exige 6 pessoas, mín. 2 coordenadores
        tarde_atribuida = []
        
        coords_ja_na_tarde = 0 # Assegurar min 2
        coords_necessarias_t = max(0, 2 - coords_ja_na_tarde)
        n_coords_t = min(coords_necessarias_t, len(coords_disp))
        tarde_atribuida.extend(coords_disp[:n_coords_t])
        coords_disp = coords_disp[n_coords_t:]

        falta_tarde = 6 - len(tarde_atribuida)
        tot_t_restantes = coords_disp + normais_disp
        tarde_atribuida.extend(tot_t_restantes[:falta_tarde])

        for e in tarde_atribuida:
            escala[e][d_idx] = "T72"

        # Qualquer restante fica de Folga (D)
        for e in todos_enfs:
            if escala[e][d_idx] == "":
                escala[e][d_idx] =
