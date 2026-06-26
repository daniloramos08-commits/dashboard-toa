import pandas as pd
import streamlit as st

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

# MAPEAR COLUNAS
col_map = {col.lower(): col for col in df.columns}

def get_col(nome):
    for c in col_map:
        if nome in c:
            return col_map[c]
    return None

col_status = get_col("status")
col_tecnico = get_col("recurso")

# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros")

df_f = df.copy()

if col_status:
    status_sel = st.sidebar.multiselect(
        "Status",
        df[col_status].dropna().unique()
    )
    if status_sel:
        df_f = df_f[df_f[col_status].isin(status_sel)]

if col_tecnico:
    tec_sel = st.sidebar.multiselect(
        "Técnico",
        df[col_tecnico].dropna().unique()
    )
    if tec_sel:
        df_f = df_f[df_f[col_tecnico].isin(tec_sel)]

st.markdown("## 📊 Painel Executivo")

# =========================
# KPIs
# =========================
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

# CARDS VISUAIS
col1.markdown(f"""
<div style='background:#1e293b;padding:20px;border-radius:10px;text-align:center'>
<h4>Total</h4>
<h2>{total}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style='background:#065f46;padding:20px;border-radius:10px;text-align:center'>
<h4>Concluídas</h4>
<h2>{concluidas}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div style='background:#7f1d1d;padding:20px;border-radius:10px;text-align:center'>
<h4>Canceladas</h4>
<h2>{canceladas}</h2>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div style='background:#1e40af;padding:20px;border-radius:10px;text-align:center'>
<h4>% Conclusão</h4>
<h2>{taxa:.1f}%</h2>
</div>
""", unsafe_allow_html=True)
# =========================
# GRÁFICOS
# =========================
st.markdown("## 📈 Análise")

colA, colB = st.columns(2)

if col_status:
    with colA:
        st.subheader("Status das Atividades")
        st.bar_chart(df_f[col_status].value_counts())

if col_tecnico:
    with colB:
        st.subheader("Top Técnicos")
        st.bar_chart(df_f[col_tecnico].value_counts().head(10))
# =========================
# BASE
# =========================
st.subheader("Base de dados")
st.markdown("## 📋 Base Detalhada")
st.dataframe(df_f, use_container_width=True, height=400)

