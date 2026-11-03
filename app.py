import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala ULS Leiria - Trabalho por Equipas", page_icon="🏥", layout="wide")

st.title("🏥 Gestor de Escalas de Enfermagem - ULS Leiria")
st.write("Escala baseada na coesão das equipas, garantindo coordenadores naturais, rácios estritos (6M / 6T / 5N) e transições legais.")

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
# 2. BASE DE DADOS DAS EQUIPAS
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

if "bloqueios" not in st.session_state:
    st.session_state["bloqueios"] = {}

if "metas_turnos" not in st.session_state:
    st.session_state["metas_turnos"] = {}

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
dias_semana_num = []
sabs_doms = []

for i in range(dias_totais):
    d_atual = data_inicio + timedelta(days=i)
    colunas_dias.append(f"{d_atual.strftime('%d/%m')} ({dias_semana_pt[d_atual.weekday()].lower()})")
    dias_semana_num.append(d_atual.weekday())
    if d_atual.weekday() == 5:
        if i + 1 < dias_totais:
            sabs_doms.append((i, i+1))

# ----------------------------------------------------
# 4. GESTÃO DE EQUIPAS, COORDENAÇÃO E TIPO DE HORÁRIO
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

# Compilar mapa de pessoal ativo e estruturas por equipa
info_enfermeiros = {}
equipas_map = {}
for eq, lista in st.session_state["equipas_dados"].items():
    equipas_map[eq] = []
    for m in lista:
        if m["ativo"]:
            info_enfermeiros[m["nome"]] = {
                "equipa": eq,
                "coordenadora": m["coordenadora"],
                "tipo_horario": m.get("tipo_horario", "Roulement")
            }
            equipas_map[eq].append(m["nome"])

todos_enfs = list(info_enfermeiros.keys())

for e in todos_enfs:
    if e not in st.session_state["metas_turnos"]:
        st.session_state["metas_turnos"][e] = 18

with st.expander("🎯 Definir Meta de Turnos Mensais por Pessoa", expanded=False):
    cols_meta = st.columns(3)
    for i, e in enumerate(todos_enfs):
        with cols_meta[i % 3]:
            st.session_state["metas_turnos"][e] = st.number_input(
                f"Meta ({e}):", min_value=0, max_value=dias_totais, 
                value=st.session_state["metas_turnos"][e], key=f"meta_t_{e}"
            )

# ----------------------------------------------------
# 5. BLOQUEIOS E RESTRIÇÕES INDIVIDUAIS (COM ELIMINAÇÃO)
# ----------------------------------------------------
st.divider()
st.subheader("📌 2. Restrições e Pedidos Individuais (Adicionar / Eliminar)")

cb1, cb2, cb3 = st.columns(3)
with cb1:
    enf_sel = st.selectbox("Enfermeiro/a:", todos_enfs)
with cb2:
    dia_sel = st.selectbox("Dia do Calendário:", colunas_dias)
with cb3:
    estado_sel = st.selectbox("Turno / Pedido Fixo:", ["D (Descanso/Folga)", "L (Férias)", "M59 (Manhã)", "T72 (Tarde)", "N4 (Noite)", "Au (Ausência)"])

sigla_est = estado_sel.split(" ")[0]

if st.button("➕ Fixar Pedido/Restrição"):
    if enf_sel not in st.session_state["bloqueios"]:
        st.session_state["bloqueios"][enf_sel] = {}
    st.session_state["bloqueios"][enf_sel][dia_sel] = sigla_est
    st.success(f"Registado rigorosamente: {enf_sel} -> {sigla_est} no dia {dia_sel}.")
    st.rerun()

if st.session_state["bloqueios"]:
    with st.expander("🗑️ Ver e Gerir Restrições Ativas (Apagar Individualmente)", expanded=True):
        remover_chave = None
        for e, r in st.session_state["bloqueios"].items():
            for d, t in r.items():
                col_r1, col_r2 = st.columns([4, 1])
                with col_r1:
                    st.text(f"• {e} | Dia: {d} | Pedido: {t}")
                with col_r2:
                    if st.button("❌ Apagar", key=f"del_{e}_{d}"):
                        remover_chave = (e, d)
        
        if remover_chave:
            e_rem, d_rem = remover_chave
            del st.session_state["bloqueios"][e_rem][d_rem]
            if not st.session_state["bloqueios"][e_rem]:
                del st.session_state["bloqueios"][e_rem]
            st.success("Restrição removida com sucesso!")
            st.rerun()

        if st.button("🗑️ Limpar Todas as Restrições"):
            st.session_state["bloqueios"] = {}
            st.rerun()

# ----------------------------------------------------
# 6. GERADOR DE ESCALA COM COESÃO DE EQUIPAS E RÁCIOS
# ----------------------------------------------------
st.divider()

if st.button("🚀 Gerar Escala Final (Equipas Unidas + Rácios 6M/6T/5N)", type="primary"):
    
    escala = {e: [""] * dias_totais for e in todos_enfs}
    
    # 1. Aplicar Pedidos e Restrições Individuais Fixas
    for e in todos_enfs:
        if e in st.session_state["bloqueios"]:
            for d_idx, d_nome in enumerate(colunas_dias):
                if d_nome in st.session_state["bloqueios"][e]:
                    escala[e][d_idx] = st.session_state["bloqueios"][e][d_nome]

    # 2. Atribuir 1 Fim de Semana Completo de Folga por Pessoa
    fds_folga_por_pessoa = {}
    if sabs_doms:
        for idx_e, e in enumerate(todos_enfs):
            fds_escolhido = sabs_doms[idx_e % len(sabs_doms)]
            sab_idx, dom_idx = fds_escolhido
            fds_folga_por_pessoa[e] = sab_idx
            if escala[e][sab_idx] == "":
                escala[e][sab_idx] = "D"
            if escala[e][dom_idx] == "":
                escala[e][dom_idx] = "D"

    amamentacao_lista = [e for e in todos_enfs if info_enfermeiros[e]["equipa"] == "Amamentação"]
    
    # 3. Pré-preencher Roulement com blocos de equipa desfasados para garantir sinergia e coordenadores
    lista_equipa_nomes = [eq for eq in equipas_map.keys() if eq not in ["Amamentação", "Outros / Especiais"]]
    
    for eq_idx, eq_nome in enumerate(lista_equipa_nomes):
        membros_eq = [m for m in equipas_map[eq_nome] if info_enfermeiros[m]["tipo_horario"] == "Roulement"]
        # Cada equipa inteira segue um offset base, mantendo os elementos da mesma equipa a trabalhar juntos
        offset_eq = (eq_idx * 3) % len(PADRAO_ROULEMENT)
        for e in membros_eq:
            for d_idx in range(dias_totais):
                if escala[e][d_idx] == "":
                    escala[e][d_idx] = PADRAO_ROULEMENT[(d_idx + offset_eq) % len(PADRAO_ROULEMENT)]

    # 4. Processamento Dia a Dia com Garantia de Rácios (6M, 6T, 5N) e Coordenadores naturais
    for d_idx in range(dias_totais):
        dia_sem_num = dias_semana_num[d_idx]
        
        # A. Descanso pós-noite obrigatório
        if d_idx > 0:
            for e in todos_enfs:
                if escala[e][d_idx - 1] == "N4" and escala[e][d_idx] == "":
                    escala[e][d_idx] = "D"

        # B. Amamentação: Máximo 3 de manhã, restante folga D
        am_disp = [e for e in amamentacao_lista if escala[e][d_idx] not in ["L", "Au", "GvR"]]
        random.shuffle(am_disp)
        am_trabalham = am_disp[:3]
        am_folgam = am_disp[3:]
        for e in am_trabalham:
            escala[e][d_idx] = "M59"
        for e in am_folgam:
            escala[e][d_idx] = "D"

        # C. Céu Peralta / Especiais
        if "Céu Peralta" in todos_enfs and escala["Céu Peralta"][d_idx] == "":
            ant_cp = escala["Céu Peralta"][d_idx - 1] if d_idx > 0 else "D"
            escala["Céu Peralta"][d_idx] = "T72" if ant_cp == "T72" else "M59"

        # --- SELEÇÃO DE NOITES (N4): Exatamente 5 elementos (mín 2 coordenadores) ---
        candidatos_n = []
        for e in todos_enfs:
            if escala[e][d_idx] != "": continue
            ant = escala[e][d_idx - 1] if d_idx > 0 else "D"
            if ant in ["M59", "T72"]: continue
            if dia_sem_num == 0 and d_idx > 0:
                sab_folga = fds_folga_por_pessoa.get(e)
                if sab_folga is not None and (d_idx - 1) == sab_folga + 1:
                    continue
            candidatos_n.append(e)

        if len(candidatos_n) < 5:
            extras_n = [e for e in todos_enfs if escala[e][d_idx] == "" and (d_idx == 0 or escala[e][d_idx-1] not in ["M59", "T72"])]
            for ex in extras_n:
                if ex not in candidatos_n: candidatos_n.append(ex)

        coords_n = [e for e in candidatos_n if info_enfermeiros[e]["coordenadora"]]
        normais_n = [e for e in candidatos_n if not info_enfermeiros[e]["coordenadora"]]

        noite_dia = []
        n_coord_n = min(2, len(coords_n))
        noite_dia.extend(coords_n[:n_coord_n])
        coords_n = coords_n[n_coord_n:]
        
        restantes_n = coords_n + normais_n
        falta_n = 5 - len(noite_dia)
        noite_dia.extend(restantes_n[:falta_n])

        for e in noite_dia:
            escala[e][d_idx] = "N4"

        # --- SELEÇÃO DE MANHÃS (M59): Exatamente 6 elementos (m
