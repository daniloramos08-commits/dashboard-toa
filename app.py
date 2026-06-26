import pandas as pd
import streamlit as st
import plotly.express as px
import unicodedata

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard TOA",
    layout="wide"
)

st.markdown(
    """
    <style>
        .main {
            background-color: #ffffff;
        }

        h1, h2, h3 {
            font-weight: 800;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Dashboard TOA")

# =========================
# CARREGAR DADOS
# =========================
df = pd.read_excel(
    "dados.xlsx",
    sheet_name="ANALÍTICO TOA",
    engine="openpyxl",
    header=11
)

# =========================
# LIMPEZA DAS COLUNAS
# =========================
df.columns = df.columns.str.strip()

# =========================
# FUNÇÃO PARA NORMALIZAR TEXTO
# =========================
def normalizar_texto(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    return texto

colunas_normalizadas = {
    normalizar_texto(col): col for col in df.columns
}

def get_col_exata(nome):
    nome_norm = normalizar_texto(nome)
    return colunas_normalizadas.get(nome_norm)

def get_col_contem(nome):
    nome_norm = normalizar_texto(nome)
    for col_norm, col_original in colunas_normalizadas.items():
        if nome_norm in col_norm:
            return col_original
    return None

# =========================
# IDENTIFICAR COLUNAS
# =========================
col_status = get_col_exata("Status") or get_col_contem("Status")
col_tecnico = get_col_exata("Recurso") or get_col_contem("Recurso")

# Área: prioriza a coluna exata ÁREA para não pegar Área de Trabalho
col_area = get_col_exata("Área") or get_col_exata("AREA")
if not col_area:
    col_area = get_col_contem("área") or get_col_contem("area") or get_col_contem("cidade")

# Atividade: prioriza Tipo de Atividade
col_atividade = (
    get_col_exata("Tipo de Atividade")
    or get_col_exata("ATIVIDADE")
    or get_col_exata("Atividade")
    or get_col_contem("tipo de atividade")
    or get_col_contem("atividade")
)

# =========================
# SIDEBAR - FILTROS EM LISTA
# =========================
st.sidebar.markdown("### 🔎 Filtros")

df_f = df.copy()

# =========================
# FILTRO STATUS
# =========================
if col_status:
    opcoes_status = ["Todos"] + sorted(df[col_status].dropna().astype(str).unique())

    status_sel = st.sidebar.selectbox(
        "Status",
        opcoes_status,
        index=0
    )

    if status_sel != "Todos":
        df_f = df_f[df_f[col_status].astype(str) == status_sel]

# =========================
# FILTRO TÉCNICO
# =========================
if col_tecnico:
    opcoes_tecnico = ["Todos"] + sorted(df[col_tecnico].dropna().astype(str).unique())

    tecnico_sel = st.sidebar.selectbox(
        "Técnico",
        opcoes_tecnico,
        index=0
    )

    if tecnico_sel != "Todos":
        df_f = df_f[df_f[col_tecnico].astype(str) == tecnico_sel]

# =========================
# FILTRO ÁREA
# =========================
if col_area:
    opcoes_area = ["Todos"] + sorted(df[col_area].dropna().astype(str).unique())

    area_sel = st.sidebar.selectbox(
        "Área",
        opcoes_area,
        index=0
    )

    if area_sel != "Todos":
        df_f = df_f[df_f[col_area].astype(str) == area_sel]

# =========================
# FILTRO ATIVIDADE
# =========================
if col_atividade:
    opcoes_atividade = ["Todos"] + sorted(df[col_atividade].dropna().astype(str).unique())

    atividade_sel = st.sidebar.selectbox(
        "Atividade",
        opcoes_atividade,
        index=0
    )

    if atividade_sel != "Todos":
        df_f = df_f[df_f[col_atividade].astype(str) == atividade_sel]

# =========================
# PAINEL EXECUTIVO
# =========================
st.markdown("## 📊 Painel Executivo")

total = len(df_f)

if col_status:
    status_norm = df_f[col_status].astype(str).apply(normalizar_texto)

    concluidas = (status_norm == "concluida").sum()
    canceladas = status_norm.str.contains("cancel", na=False).sum()
    suspensas = status_norm.str.contains("suspens", na=False).sum()
    nao_concluidas = status_norm.str.contains("nao conclu", na=False).sum()
else:
    concluidas = 0
    canceladas = 0
    suspensas = 0
    nao_concluidas = 0

taxa_conclusao = (concluidas / total * 100) if total else 0

col1, col2, col3, col4 = st.columns(4)

col1.markdown(
    f"<div style='background:#1e293b;padding:22px;border-radius:12px;text-align:center;color:white'>"
    f"<h4 style='font-weight:bold;color:white'>Total</h4>"
    f"<h2 style='font-weight:bold;color:white'>{total}</h2>"
    f"</div>",
    unsafe_allow_html=True
)

col2.markdown(
    f"<div style='background:#065f46;padding:22px;border-radius:12px;text-align:center;color:white'>"
    f"<h4 style='font-weight:bold;color:white'>Concluídas</h4>"
    f"<h2 style='font-weight:bold;color:white'>{concluidas}</h2>"
    f"</div>",
    unsafe_allow_html=True
)

col3.markdown(
    f"<div style='background:#7f1d1d;padding:22px;border-radius:12px;text-align:center;color:white'>"
    f"<h4 style='font-weight:bold;color:white'>Canceladas</h4>"
    f"<h2 style='font-weight:bold;color:white'>{canceladas}</h2>"
    f"</div>",
    unsafe_allow_html=True
)

col4.markdown(
    f"<div style='background:#1e40af;padding:22px;border-radius:12px;text-align:center;color:white'>"
    f"<h4 style='font-weight:bold;color:white'>% Conclusão</h4>"
    f"<h2 style='font-weight:bold;color:white'>{taxa_conclusao:.1f}%</h2>"
    f"</div>",
    unsafe_allow_html=True
)

st.divider()

# =========================
# GRÁFICOS PRINCIPAIS
# =========================
st.markdown("## 📈 Análise Operacional")

graf1, graf2 = st.columns(2)

# =========================
# GRÁFICO STATUS
# =========================
if col_status:
    with graf1:
        st.subheader("Status das Atividades")

        data_status = (
            df_f[col_status]
            .dropna()
            .astype(str)
            .value_counts()
            .reset_index()
        )

        data_status.columns = ["Status", "Quantidade"]

        fig_status = px.bar(
            data_status,
            x="Status",
            y="Quantidade",
            text="Quantidade",
            color="Status"
        )

        fig_status.update_layout(
            height=420,
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(showgrid=False, visible=False),
            xaxis=dict(showgrid=False),
            margin=dict(l=10, r=10, t=30, b=80)
        )

        fig_status.update_traces(textposition="outside")

        st.plotly_chart(
            fig_status,
            use_container_width=True,
            key="grafico_status"
        )

# =========================
# GRÁFICO TOP TÉCNICOS
# =========================
# =========================
# GRÁFICO TOP TÉCNICOS
# =========================
if col_tecnico:
    with graf2:
        st.subheader("Top Técnicos")

        data_tecnico = (
            df_f[col_tecnico]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
            .sort_values(ascending=True)  # deixa o maior no topo no gráfico horizontal
            .reset_index()
        )

        data_tecnico.columns = ["Técnico", "Quantidade"]

        fig_tecnico = px.bar(
            data_tecnico,
            x="Quantidade",
            y="Técnico",
            text="Quantidade",
            orientation="h",
            color="Quantidade",
            color_continuous_scale="Blues"
        )

        fig_tecnico.update_layout(
            height=420,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title=None,
            yaxis_title=None,
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(
                showgrid=False,
                categoryorder="array",
                categoryarray=data_tecnico["Técnico"].tolist()
            ),
            margin=dict(l=10, r=10, t=30, b=30)
        )

        fig_tecnico.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig_tecnico,
            use_container_width=True,
            key="grafico_tecnico"
        )

        data_tecnico = (
            df_f[col_tecnico]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
            .reset_index()
        )

        data_tecnico.columns = ["Técnico", "Quantidade"]

        fig_tecnico = px.bar(
            data_tecnico,
            x="Quantidade",
            y="Técnico",
            text="Quantidade",
            orientation="h",
            color="Quantidade",
            color_continuous_scale="Blues"
        )

        fig_tecnico.update_layout(
            height=420,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title=None,
            yaxis_title=None,
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False),
            margin=dict(l=10, r=10, t=30, b=30)
        )

        fig_tecnico.update_traces(textposition="outside")

        st.plotly_chart(
            fig_tecnico,
            use_container_width=True,
            key="grafico_tecnico"
        )

st.divider()

# =========================
# STATUS POR ÁREA
# =========================
if col_status and col_area:
    st.markdown("## 📊 Status por Área")

    df_area_status = (
        df_f
        .groupby([col_area, col_status])
        .size()
        .reset_index(name="Quantidade")
    )

    top_areas = (
        df_area_status
        .groupby(col_area)["Quantidade"]
        .sum()
        .nlargest(15)
        .index
    )

    df_area_status = df_area_status[df_area_status[col_area].isin(top_areas)]

    fig_area = px.bar(
        df_area_status,
        x=col_area,
        y="Quantidade",
        color=col_status,
        text="Quantidade",
        barmode="stack"
    )

    fig_area.update_layout(
        height=520,
        showlegend=True,
        legend_title="Status",
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(showgrid=False, visible=False),
        xaxis=dict(showgrid=False, tickangle=-45),
        margin=dict(l=10, r=10, t=40, b=120)
    )

    fig_area.update_traces(textposition="inside")

    st.plotly_chart(
        fig_area,
        use_container_width=True,
        key="grafico_status_area"
    )

st.divider()

# =========================
# ATIVIDADES POR ÁREA
# =========================
if col_atividade and col_area:
    st.markdown("## 📌 Atividades por Área")

    df_atividade_area = (
        df_f
        .groupby([col_area, col_atividade])
        .size()
        .reset_index(name="Quantidade")
    )

    top_areas_atividade = (
        df_atividade_area
        .groupby(col_area)["Quantidade"]
        .sum()
        .nlargest(15)
        .index
    )

    df_atividade_area = df_atividade_area[df_atividade_area[col_area].isin(top_areas_atividade)]

    fig_atividade_area = px.bar(
        df_atividade_area,
        x=col_area,
        y="Quantidade",
        color=col_atividade,
        text="Quantidade",
        barmode="stack"
    )

    fig_atividade_area.update_layout(
        height=520,
        showlegend=True,
        legend_title="Atividade",
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(showgrid=False, visible=False),
        xaxis=dict(showgrid=False, tickangle=-45),
        margin=dict(l=10, r=10, t=40, b=120)
    )

    fig_atividade_area.update_traces(textposition="inside")

    st.plotly_chart(
        fig_atividade_area,
        use_container_width=True,
        key="grafico_atividade_area"
    )

st.divider()

# =========================
# BASE DETALHADA
# =========================
st.markdown("## 📋 Base Detalhada")

st.dataframe(
    df_f,
    use_container_width=True,
    height=420
)
