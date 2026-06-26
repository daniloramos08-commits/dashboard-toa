import pandas as pd
import streamlit as st
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")

# TEMA
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
# SIDEBAR
# =========================
st.sidebar.markdown("### 🔎 Filtros")

df_f = df.copy()

if col_status:
    opcoes_status = df[col_status].dropna().unique()
    status_sel = st.sidebar.multiselect(
        "Status",
        opcoes_status,
        default=opcoes_status,
        placeholder="Escolha uma opção"
    )

    if status_sel:
        df_f = df_f[df_f[col_status].isin(status_sel)]

if col_tecnico:
    opcoes_tec = df[col_tecnico].dropna().unique()
    tec_sel = st.sidebar.multiselect(
        "Técnico",
        opcoes_tec,
        default=opcoes_tec,
        placeholder="Escolha uma opção"
    )

    if tec_sel:
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
col1.markdown(f"""
<div style='background:#1e293b;padding:20px;border-radius:10px;text-align:center;color:white'>
<h4 style='font-weight:bold'>Total</h4>
<h2 style='font-weight:bold'>{total}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style='background:#065f46;padding:20px;border-radius:10px;text-align:center;color:white'>
<h4 style='font-weight:bold'>Concluídas</h4>
<h2 style='font-weight:bold'>{concluidas}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div style='background:#7f1d1d;padding:20px;border-radius:10px;text-align:center;color:white'>
<h4 style='font-weight:bold'>Canceladas</h4>
<h2 style='font-weight:bold'>{canceladas}</h2>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div style='background:#1e40af;padding:20px;border-radius:10px;text-align:center;color:white'>
<h4 style='font-weight:bold'>% Conclusão</h4>
<h2 style='font-weight:bold'>{taxa:.1f}%</h2>
</div>
""", unsafe_allow_html=True)

st.divider()

# =========================
# GRÁFICOS
# =========================
st.markdown("## 📈 Análise")

colA, colB = st.columns(2)

if col_status:
    with colA:
        st.subheader("Status das Atividades")

        data_status = df_f[col_status].value_counts().reset_index()
        data_status.columns = ["Status", "Quantidade"]

        fig = px.bar(
            data_status,
            x="Status",
            y="Quantidade",
            text="Quantidade",
            color="Status"
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(showgrid=False, visible=False),
            xaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

if col_tecnico:
    with colB:
        st.subheader("Top Técnicos")

        data_tec = df_f[col_tecnico].value_counts().head(10).reset_index()
        data_tec.columns = ["Tecnico", "Quantidade"]

        fig2 = px.bar(
            data_tec,
            x="Tecnico",
            y="Quantidade",
            text="Quantidade",
            color="Quantidade",
            color_continuous_scale="Blues"
        )

        fig2.update_layout(
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(showgrid=False, visible=False),
            xaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig2, use_container_width=True)

# =========================
# BASE
# =========================
st.markdown("## 📋 Base Detalhada")
st.dataframe(df_f, use_container_width=True, height=400)
