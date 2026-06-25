import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("📊 Dashboard TOA")

# CARREGAR DADOS
df = pd.read_excel("dados.xlsx", sheet_name="ANALÍTICO TOA", engine="openpyxl")

# TRATAMENTO
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["TEMPO TOTAL"] = pd.to_timedelta(df["TEMPO TOTAL"], errors="coerce")

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Total", len(df))
col2.metric("Concluídas", df[df["Status"] == "Concluída"].shape[0])
col3.metric("Canceladas", df[df["Status"] == "Cancelada"].shape[0])

# GRÁFICOS
st.subheader("Status")
st.bar_chart(df["Status"].value_counts())

st.subheader("Top Técnicos")
st.bar_chart(df["Recurso"].value_counts().head(10))

st.subheader("Causas")
st.bar_chart(df["Causa 1"].value_counts().head(10))

st.subheader("Base")
st.dataframe(df)
