import pandas as pd
import streamlit as st
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    body {
        background-color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
col_area = get_col("cidade")


# =========================
# FILTROS
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

# CARDS (SEM ERRO DE STRING)
col1.markdown(
    f"<div style='background:#1e293b;padding:20px;border-radius:10px;text-align:center;color:white'>"
    f"<h4>Total</h4><h2>{total}</h2></div>",
    unsafe_allow_html=True
)

col2.markdown(
    f"<div style='background:#065f46;padding:20px;border-radius:10px;text-align:center;color:white'>"
    f"<h4>Concluídas</h4><h2>{concluidas}</h2></div>",
    unsafe_allow_html=True
)

col3.markdown(
    f"<div style='background:#7f1d1d;padding:20px;border-radius:10px;text-align:center;color:white'>"
    f"<h4>Canceladas</h4><h2>{canceladas}</h2></div>",
    unsafe_allow_html=True
)

col4.markdown(
    f"<div style='background:#1e40af;padding:20px;border-radius:10px;text-align:center;color:white'>"
    f"<h4>% Conclusão</h4><h2>{taxa:.1f}%</h2></div>",
    unsafe_allow_html=True
)

st.divider()

# =========================

# =========================
# =========================
# STATUS POR ÁREA
# =========================
if col_status and col_area:
    st.markdown("## 📊 Status por Área")

    df_group = df_f.groupby([col_area, col_status]).size().reset_index(name="Quantidade")

    fig3 = px.bar(
        df_group,
        x=col_area,
        y="Quantidade",
        color=col_status,
        barmode="group",
        text="Quantidade"
    )

    fig3.update_layout(
        height=500,  # 🔥 resolve o problema de gráfico achatado
        showlegend=True,
        legend_title="Status",
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(showgrid=False, visible=False),
        xaxis=dict(showgrid=False),
        margin=dict(l=10, r=10, t=40, b=80)
    )

    fig3.update_traces(textposition="outside")

    st.plotly_chart(fig3, use_container_width=True, key="grafico_area")

    st.plotly_chart(fig3, use_container_width=True)
