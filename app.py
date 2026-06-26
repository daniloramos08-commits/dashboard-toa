import pandas as pd
import streamlit as st
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")

st.markdown("""
<style>
body {
    background-color: #0f172a;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard TOA")

# =========================
# LOAD
# =========================
df = pd.read_excel(
    "dados.xlsx",
    sheet_name="ANALÍTICO TOA",
    engine="openpyxl",
    header=11
)

# =========================
# LIMPEZA
# =========================
df.columns = df.columns.str.strip()

col_map = {col.lower(): col for col in df.columns}

def get_col(nome):
    for c in col_map:
        if nome in c:
            return col_map[c]
    return None

col_status = get_col("status")
col_tecnico = get_col("recurso")

# =========================
# FILTROS PROFISSIONAIS
# =========================
st.sidebar.markdown("### 🔎 Filtros")

df_f = df.copy()

# STATUS
if col_status:
    st.sidebar.markdown("**Status**")
    
    opcoes_status = df[col_status].dropna().unique()
    
    selecionar_todos_status = st.sidebar.checkbox(
        "Selecionar todos (Status)",
        value=True
    )
    
    if selecionar_todos_status:
        status_sel = opcoes_status
    else:
        status_sel = st.sidebar.multiselect(
            "",
            opcoes_status,
            placeholder="Escolha uma opção"
        )

    df_f = df_f[df_f[col_status].isin(status_sel)]

# TÉCNICO
if col_tecnico:
    st.sidebar.markdown("**Técnico**")
    
    opcoes_tec = df[col_tecnico].dropna().unique()
    
    selecionar_todos_tec = st.sidebar.checkbox(
        "Selecionar todos (Técnico)",
        value=True
    )
    
    if selecionar_todos_tec:
        tec_sel = opcoes_tec
    else:
        tec_sel = st.sidebar.multiselect(
            "",
            opcoes_tec,
            placeholder="Escolha uma opção"
        )

    df_f = df_f[df_f[col_tecnico].isin(tec_sel)]

# =========================
# KPIs
# =========================
st.markdown("## 📊 Painel Executivo")

col1, col2, col3, col4 = st.columns(4)

total = len(df_f)

if col_status:
    status_series = df_f[col_status].astype(str).str.strip().str.lower()
    concluidas = status_series.str.contains("conclu").sum()
    canceladas = status_series.str.contains("cancel").sum()
else:
    concluidas = 0
    canceladas = 0

taxa = (concluidas / total * 100) if total else 0

# CARDS
col1.markdown(f""")
<div style='background:#1e293b;padding:20px;border-radius:10px;text-align:center;color:white'>
<h4 style='font-weight:bold'>Total</h4>
<h2 style='font-weight:bold'>{total}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f""")
<div style='background:#065f46;padding:20px;border-radius:10px;text-align:center;color:white'>
<h4 style='font-weight:bold'>Concluídas</h4>
<h2 style='font-weight:bold'>{concluidas}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f""")
<div style='background:#7f1d1d;padding:20px;border-radius:10px;text-align:center;color:white'>
