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

        div[data-testid="stMetric"] {
            background-color: #1e293b;
            padding: 20px;
            border-radius: 12px;
            color: white;
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
# IDENTIFICAR COLUNAS PRINCIPAIS
# =========================
col_status = get_col_exata("Status") or get_col_contem("Status")
col_tecnico = get_col_exata("Recurso") or get_col_contem("Recurso")

# IMPORTANTE:
# Primeiro tenta achar a coluna exata "ÁREA".
# Isso evita pegar "Área de Trabalho" ou "Área de Deslocamento".
col_area = get_col_exata("Área") or get_col_exata("AREA")

# Se não achar "ÁREA", tenta alternativas.
if not col_area:
    col_area = get_col_contem("área") or get_col_contem("area") or get_col_contem("cidade")

# =========================
# SIDEBAR - FILTROS
# =========================
st.sidebar.markdown("### 🔎 Filtros")

df_f = df.copy()

# =========================
# FILTRO STATUS
# =========================
if col_status:
    st.sidebar.markdown("**Status**")

    opcoes_status = sorted(df[col_status].dropna().astype(str).unique())

    selecionar_todos_status = st.sidebar.checkbox(
        "Selecionar todos (Status)",
        value=True
    )

    if selecionar_todos_status:
        status_sel = opcoes_status
    else:
        status_sel = st.sidebar.multiselect(
            "Escolha uma opção",
            opcoes_status,
            placeholder="Escolha uma opção"
        )

    if status_sel:
        df_f = df_f[df_f[col_status].astype(str).isin(status_sel)]
    else:
        df_f = df_f.iloc[0:0]

# =========================
# FILTRO TÉCNICO
# =========================
if col_tecnico:
    st.sidebar.markdown("**Técnico**")

    opcoes_tecnico = sorted(df[col_tecnico].dropna().astype(str).unique())

    selecionar_todos_tecnico = st.sidebar.checkbox(
        "Selecionar todos (Técnico)",
        value=True
    )

    if selecionar_todos_tecnico:
        tecnico_sel = opcoes_tecnico
    else:
        tecnico_sel = st.sidebar.multiselect(
            "Escolha uma opção ",
            opcoes_tecnico,
            placeholder="Escolha uma opção"
        )

    if tecnico_sel:
        df_f = df_f[df_f[col_tecnico].astype(str).isin(tecnico_sel)]
    else:
        df_f = df_f.iloc[0:0]

# =========================
# FILTRO ÁREA
# =========================
if col_area:
    st.sidebar.markdown("**Área**")

    opcoes_area = sorted(df[col_area].dropna().astype(str).unique())

    selecionar_todos_area = st.sidebar.checkbox(
        "Selecionar todos (Área)",
        value=True
    )

    if selecionar_todos_area:
        area_sel = opcoes_area
    else:
        area_sel = st.sidebar.multiselect(
            "Escolha uma opção  ",
            opcoes_area,
            placeholder="Escolha uma opção"
        )

    if area_sel:
        df_f = df_f[df_f[col_area].astype(str).isin(area_sel)]
    else:
        df_f = df_f.iloc[0:0]

# =========================
# PAINEL EXECUTIVO
# =========================
st.markdown("## 📊 Painel Executivo")

total = len(df_f)

if col_status:
    status_series = df_f[col_status].astype(str).str.strip().str.lower()

    concluidas = status_series.str.contains("conclu", na=False).sum()
    canceladas = status_series.str.contains("cancel", na=False).sum()
    suspensas = status_series.str.contains("suspens", na=False).sum()
    nao_concluidas = status_series.str.contains("não conclu|nao conclu", na=False).sum()
else:
    concluidas = 0
    canceladas = 0
    suspensas = 0
    nao_concluidas = 0

taxa_conclusao = (concluidas / total * 100) if total else 0

col1, col2, col3, col4 = st.columns(4)

col1.markdown(
    f"""
    <div style='background:#1e293b;padding:22px;border-radius:12px;text-align:center;color:white'>
        <h4 style='font-weight:bold;color:white'>Total</h4>
        <h2 style='font-weight:bold;color:white'>{total}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

col2.markdown(
    f"""
    <div style='background:#065f46;padding:22px;border-radius:12px;text-align:center;color:white'>
        <h4 style='font-weight:bold;color:white'>Concluídas</h4>
        <h2 style='font-weight:bold;color:white'>{concluidas}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

col3.markdown(
    f"""
    <div style='background:#7f1d1d;padding:22px;border-radius:12px;text-align:center;color:white'>
        <h4 style='font-weight:bold;color:white'>Canceladas</h4>
        <h2 style='font-weight:bold;color:white'>{canceladas}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

col4.markdown(
    f"""
    <div style='background:#1e40af;padding:22px;border-radius:12px;text-align:center;color:white'>
        <h4 style='font-weight:bold;color:white'>% Conclusão</h4>
        <h2 style='font-weight:bold;color:white'>{taxa_conclusao:.1f}%</h2>
    </div>
    """,
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
if col_tecnico:
    with graf2:
        st.subheader("Top Técnicos")

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

    # Se tiver muita área, mostra apenas as 15 principais para não ficar poluído
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
# BASE DETALHADA
# =========================
st.markdown("## 📋 Base Detalhada")
st.dataframe(
    df_f,
    use_container_width=True,
    height=420
)
