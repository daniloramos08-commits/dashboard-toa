import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("📊 Dashboard TOA")

# =========================
# CARREGAR DADOS
# =========================
df = pd.read_excel(
    "dados.xlsx",
    sheet_name="ANALÍTICO TOA",
    engine="openpyxl",
    header=11   # 👈 ESSA LINHA É A CHAVE
)

# =========================
# LIMPEZA (ESSENCIAL)
# =========================
df.columns = df.columns.str.strip()

# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros")

df_f = df.copy()

if col_status:
    status_sel = st.sidebar.multiselect("Status", df_f[col_status].unique())

    if status_sel:
        df_f = df_f[df_f[col_status].isin(status_sel)]

if col_tecnico:
    tec_sel = st.sidebar.multiselect("Técnico", df[col_tecnico].unique())

    if tec_sel:
        df_f = df_f[df_f[col_tecnico].isin(tec_sel)]

# padronizar nomes para busca
col_map = {col.lower(): col for col in df.columns}

def get_col(nome):
    for c in col_map:
        if nome in c:
            return col_map[c]
    return None

col_status = get_col("status")
col_tecnico = get_col("recurso")
col_tipo = get_col("atividade")
col_causa = get_col("causa")
col_tempo = get_col("duração")

# =========================
# KPIs
# =========================
col1, col2, col3 = st.columns(3)

total = len(df_f)


if col_status:

    status_series = df_f[col_status].astype(str).str.strip().str.lower()

    concluidas = status_series.str.contains("conclu").sum()
    canceladas = status_series.str.contains("cancel").sum()

else:
    concluidas = 0
    canceladas = 0


col1.metric("Total", total)
taxa = (concluidas / total * 100) if total else 0
st.metric("% Conclusão", f"{taxa:.1f}%")
``
col2.metric("Concluídas", concluidas)
col3.metric("Canceladas", canceladas)

st.divider()

# =========================
# GRÁFICOS
# =========================
if col_tecnico:
    st.subheader("Top Técnicos")
    st.bar_chart(df_f[col_tecnico].value_counts().head(10))
if col_status:
    st.subheader("Status")
    st.bar_chart(df_f[col_status].value_counts())

if col_tecnico:
    st.subheader("Top Técnicos")
    st.bar_chart(df[col_tecnico].value_counts().head(10))

if col_tipo:
    st.subheader("Tipo de Atividade")
    st.bar_chart(df[col_tipo].value_counts())

# =========================
# BASE
# =========================
st.subheader("Base de dados")
st.dataframe(df_f, use_container_width=True)
