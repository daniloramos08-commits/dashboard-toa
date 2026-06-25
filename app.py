import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

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

col1.metric("Total", total)
col2.metric("Concluídas", concluidas)
col3.metric("Canceladas", canceladas)
col4.metric("% Conclusão", f"{taxa:.1f}%")

st.divider()

# =========================
# GRÁFICOS
# =========================
if col_status:
    st.subheader("Status")
    st.bar_chart(df_f[col_status].value_counts())

if col_tecnico:
    st.subheader("Top Técnicos")
    st.bar_chart(df_f[col_tecnico].value_counts().head(10))

# =========================
# BASE
# =========================
st.subheader("Base de dados")
st.dataframe(df_f, use_container_width=True)
``
