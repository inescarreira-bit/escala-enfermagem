import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

st.set_page_config(page_title="Escala ULS Leiria - Rigor Total", page_icon="🏥", layout="wide")

st.title("🏥 Gestor de Escalas de Enfermagem - Proteção de Fins de Semana (ULS Leiria)")
st.write("Cumprimento estrito de rácios (6M / 6T / 5N), 2 Coordenadores/turno, Proteção Pós-Fim de Semana e Respeito a Bloqueios.")

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
        {"nome": "Céu Peralta", "coordenadora": False, "ativo": True},
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
dias_semana_num = [] # Guarda o número do dia da semana (0 = Seg, 6 = Dom)

sabs_doms = []
for i in range(dias_totais):
    d_atual = data_inicio + timedelta(days=i)
    colunas_dias.append(f"{d_atual.strftime('%d/%m')} ({dias_semana_pt[d_atual.weekday()].lower()})")
    dias_semana_num.append(d_atual.weekday())
    if d_atual.weekday() == 5: # Sábado
        if i + 1 < dias_totais:
            sabs_doms.append((i, i+1))

# ----------------------------------------------------
# 4. GESTÃO DE EQUIPAS
# ----------------------------------------------------
st.subheader("👥 1. Gestão de Equipas e Estatutos")

with st.expander("⚙️ Gerir Elementos, Ativar/Inativar", expanded=False):
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
# 6. GERADOR COM REGRA DE SEGURANÇA SEGUNDA-FEIRA N
# ----------------------------------------------------
st.divider()

if st.button("🚀 Gerar Escala com Proteção de Fins de Semana", type="primary"):
    
    escala = {e: [""] * dias_totais for e in todos_enfs}
    
    # 1. Aplicar Bloqueios Manuais
    for e in todos_enfs:
        if e in st.session_state["bloqueios"]:
            for d_idx, d_nome in enumerate(colunas_dias):
                if d_nome in st.session_state["bloqueios"][e]:
                    escala[e][d_idx] = st.session_state["bloqueios"][e][d_nome]

    # 2. Atribuir 1 Fim de Semana Completo de Folga por Pessoa
    if sabs_doms:
        for idx_e, e in enumerate(todos_enfs):
            fds_escolhido = sabs_doms[idx_e % len(sabs_doms)]
            sab_idx, dom_idx = fds_escolhido
            if escala[e][sab_idx] == "":
                escala[e][sab_idx] = "D"
            if escala[e][dom_idx] == "":
                escala[e][dom_idx] = "D"

    # 3. Processamento Diário com Proteção Pós-Fim de Semana
    amamentacao_lista = [e for e in todos_enfs if info_enfermeiros[e]["equipa"] == "Amamentação"]
    ceu_peralta = ["Céu Peralta"] if "Céu Peralta" in todos_enfs else []

    for d_idx in range(dias_totais):
        dia_sem_num = dias_semana_num[d_idx] # 0 = Seg, 6 = Dom
        
        disponiveis = [e for e in todos_enfs if escala[e][d_idx] == ""]
        
        # 🛡️ REGRA DE PROTEÇÃO: Se hoje é Segunda-feira (0), QUEM TEVE FOLGA NO DOMINGO (d_idx-1) NÃO PODE FAZER NOITE (N4)
        aptos_para_noite = []
        for e in disponiveis:
            if dia_sem_num == 0 and d_idx > 0: # Segunda-feira
                if escala[e][d_idx - 1] in ["D", "L", "Au", "GvR"]:
                    continue # Excluído da Noite de Segunda para proteger o descanso do Fim de Semana!
            aptos_para_noite.append(e)

        coords_noite = [e for e in aptos_para_noite if info_enfermeiros[e]["coordenadora"]]
        normais_noite = [e for e in aptos_para_noite if not info_enfermeiros[e]["coordenadora"]]

        # ----------------- NOITE (N4): Exige 5 pessoas (mín. 2 coordenadores)
        noite_atribuida = []
        n_coords_noite = min(2, len(coords_noite))
        noite_atribuida.extend(coords_noite[:n_coords_noite])
        
        tot_noite_disp = [e for e in aptos_para_noite if e not in noite_atribuida]
        falta_noite = 5 - len(noite_atribuida)
        noite_atribuida.extend(tot_noite_disp[:falta_noite])

        for e in noite_atribuida:
            escala[e][d_idx] = "N4"

        # Regra de Segurança Pós-Noite: dia seguinte é obrigatoriamente Descanso (D)
        if d_idx + 1 < dias_totais:
            for e in noite_atribuida:
                if escala[e][d_idx + 1] == "":
                    escala[e][d_idx + 1] = "D"

        # Atualizar disponíveis para o resto do dia
        disponiveis = [e for e in todos_enfs if escala[e][d_idx] == ""]
        coords_disp = [e for e in disponiveis if info_enfermeiros[e]["coordenadora"]]
        normais_disp = [e for e in disponiveis if not info_enfermeiros[e]["coordenadora"]]

        # ----------------- MANHÃ (M59): Exige 6 pessoas (máx. 3 amamentação, mín. 2 coordenadores)
        manha_atribuida = []
        am_disp = [e for e in amamentacao_lista if escala[e][d_idx] == ""]
        manha_atribuida.extend(am_disp[:3])
        
        if "Céu Peralta" in normais_disp and len(manha_atribuida) < 6:
            manha_atribuida.append("Céu Peralta")
            normais_disp.remove("Céu Peralta")

        coords_ja_m = sum(1 for e in manha_atribuida if info_enfermeiros[e]["coordenadora"])
        coords_nec_m = max(0, 2 - coords_ja_m)
        n_coords_m = min(coords_nec_m, len(coords_disp))
        
        manha_atribuida.extend(coords_disp[:n_coords_m])
        coords_disp = coords_disp[n_coords_m:]

        falta_m = 6 - len(manha_atribuida)
        tot_m_restantes = coords_disp + normais_disp
        manha_atribuida.extend(tot_m_restantes[:falta_m])

        for e in manha_atribuida:
            escala[e][d_idx] = "M59"
            if e in coords_disp: coords_disp.remove(e)
            elif e in normais_disp: normais_disp.remove(e)

        # ----------------- TARDE (T72): Exige 6 pessoas (mín. 2 coordenadores)
        disponiveis = [e for e in todos_enfs if escala[e][d_idx] == ""]
        coords_disp = [e for e in disponiveis if info_enfermeiros[e]["coordenadora"]]
        normais_disp = [e for e in disponiveis if not info_enfermeiros[e]["coordenadora"]]

        tarde_atribuida = []
        n_coords_t = min(2, len(coords_disp))
        tarde_atribuida.extend(coords_disp[:n_coords_t])
        coords_disp = coords_disp[n_coords_t:]

        falta_t = 6 - len(tarde_atribuida)
        tot_t_restantes = coords_disp + normais_disp
        tarde_atribuida.extend(tot_t_restantes[:falta_t])

        for e in tarde_atribuida:
            escala[e][d_idx] = "T72"

        # Preencher restantes com Folga (D)
        for e in todos_enfs:
            if escala[e][d_idx] == "":
                escala[e][d_idx] = "D"

    # Construção do DataFrame Final
    df_escala = pd.DataFrame(escala, index=colunas_dias).T
    df_escala.insert(0, "Coordenadora", [ "Sim" if info_enfermeiros[e]["coordenadora"] else "Não" for e in df_escala.index ])
    df_escala.insert(0, "Equipa", [ info_enfermeiros[e]["equipa"] for e in df_escala.index ])

    st.subheader("📊 Tabela Completa da Escala (Com Proteção de Segunda-Feira N)")
    st.dataframe(df_escala, use_container_width=True)

    # Validação de Rácios Diários
    st.divider()
    st.subheader("📈 Validação Rigorosa de Rácios")
    
    m_c, t_c, n_c = [], [], []
    cm_c, ct_c, cn_c = [], [], []

    for d_nome in colunas_dias:
        col = df_escala[d_nome]
        m_enfs = col[col == "M59"].index
        t_enfs = col[col == "T72"].index
        n_enfs = col[col == "N4"].index
        
        m_c.append(len(m_enfs))
        t_c.append(len(t_enfs))
        n_c.append(len(n_enfs))
        
        cm_c.append(sum(1 for e in m_enfs if info_enfermeiros[e]["coordenadora"]))
        ct_c.append(sum(1 for e in t_enfs if info_enfermeiros[e]["coordenadora"]))
        cn_c.append(sum(1 for e in n_enfs if info_enfermeiros[e]["coordenadora"]))

    df_validacao = pd.DataFrame({
        "Manhãs (M) [Obrig: 6]": m_c,
        "Coordenadores M [Min: 2]": cm_c,
        "Tardes (T) [Obrig: 6]": t_c,
        "Coordenadores T [Min: 2]": ct_c,
        "Noites (N) [Obrig: 5]": n_c,
        "Coordenadores N [Min: 2]": cn_c,
    }, index=colunas_dias)

    st.dataframe(df_validacao.T, use_container_width=True)

    # Botão de Exportação
    csv = df_escala.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Descarregar Escala em CSV / Excel",
        data=csv,
        file_name="escala_uls_leiria_protecao_fds.csv",
        mime="text/csv"
    )

# ----------------------------------------------------
# 7. LEGENDA
# ----------------------------------------------------
st.divider()
st.subheader("📖 Legenda de Turnos")
cl1, cl2 = st.columns(2)
itens = list(TURNOS_CONFIG.items())
metade = len(itens) // 2

with cl1:
    for k, v in itens[:metade]:
        st.write(f"**{k}**: {v}")
with cl2:
    for k, v in itens[metade:]:
        st.write(f"**{k}**: {v}")
