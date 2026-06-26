import pandas as pd
import streamlit as st
import plotly.express as px
import unicodedata
import streamlit.components.v1 as components
# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard TOA",
    layout="wide"
)

# =========================
# ESTILO VISUAL
# =========================
st.markdown(
    """
    <style>
        .main {
            background-color: #ffffff;
        }

        h1, h2, h3 {
            font-weight: 800;
        }

        section[data-testid="stSidebar"] {
            background-color: #f1f5f9;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# CONSTANTES
# =========================
ARQUIVO = "dados.xlsx"
ABA_ANALITICO = "ANALÍTICO TOA"
ABA_WFM = "INDICADORES WFM TOA"

# =========================
# FUNÇÕES AUXILIARES
# =========================
def normalizar_texto(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    return texto


@st.cache_data
def carregar_excel_abas():
    xls = pd.ExcelFile(ARQUIVO, engine="openpyxl")
    return xls.sheet_names


@st.cache_data
def carregar_analitico():
    df = pd.read_excel(
        ARQUIVO,
        sheet_name=ABA_ANALITICO,
        engine="openpyxl",
        header=11
    )
    df.columns = df.columns.str.strip()
    return df


def criar_card(coluna, titulo, valor, cor):
    coluna.markdown(
        f"""
        <div style='background:{cor};padding:22px;border-radius:12px;text-align:center;color:white'>
            <h4 style='font-weight:bold;color:white'>{titulo}</h4>
            <h2 style='font-weight:bold;color:white'>{valor}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )


def valor_para_float(valor):
    try:
        return float(str(valor).replace("%", "").replace(",", "."))
    except:
        return 0


def cor_celula(titulo, valor, meta):
    v = valor_para_float(valor)
    m = valor_para_float(meta)

    if ">" in titulo:
        return "#c6efce" if v >= m else "#ffc7ce"
    else:
        return "#c6efce" if v <= m else "#ffc7ce"


def montar_tabela_indicador(indicador):
    titulo = indicador["titulo"]
    meta = indicador["meta"]
    valores = indicador["valores"]

    meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN"]
    regionais = ["SPC", "SP1", "SP2", "SP3", "SP4"]

    html = f"""
    <div style="
        border:2px solid black;
        margin-bottom:18px;
        background:white;
        box-shadow:0 2px 6px rgba(0,0,0,0.18);
    ">
        <table style="
            border-collapse:collapse;
            width:100%;
            font-family:Arial;
            font-size:13px;
            text-align:center;
        ">
            <tr>
                <th rowspan="3" style="
                    background:#f4b183;
                    color:#c00000;
                    width:130px;
                    border:1px solid black;
                    font-weight:bold;
                    writing-mode:vertical-rl;
                    transform:rotate(180deg);
                    font-size:13px;
                ">
                    {titulo}
                </th>
                <th rowspan="2" style="background:#c00000;color:white;border:1px solid black;">REGIONAL</th>
                <th rowspan="2" style="background:#c00000;color:white;border:1px solid black;">META</th>
                <th colspan="6" style="background:#c00000;color:white;border:1px solid black;">{titulo}</th>
            </tr>
            <tr>
                <th colspan="6" style="background:#c00000;color:white;border:1px solid black;">2026</th>
            </tr>
            <tr>
    """

    for mes in meses:
        html += f"<th style='background:#0070c0;color:white;border:1px solid black;'>{mes}</th>"

    html += "</tr>"

    for regional in regionais:
        html += "<tr>"

        html += f"""
            <td style='border:1px solid black;font-weight:bold;background:#f2f2f2'>
                {regional}
            </td>
        """

        if regional == "SPC":
            html += f"""
                <td rowspan='5' style='border:1px solid black;font-weight:bold;background:white'>
                    {meta}
                </td>
            """

        for valor in valores.get(regional, ["0,00%"] * 6):
            cor = cor_celula(titulo, valor, meta)
            html += f"""
                <td style='border:1px solid black;background:{cor};'>
                    {valor}
                </td>
            """

        html += "</tr>"

    html += """
        </table>
    </div>
    """

    return html


# =========================
# NAVEGAÇÃO
# =========================
st.sidebar.markdown("### 📌 Navegação")

pagina = st.sidebar.radio(
    "Selecione a página",
    [
        "Dashboard TOA",
        "Indicadores WFM TOA"
    ]
)

# =========================
# VALIDAR ABAS
# =========================
try:
    abas_disponiveis = carregar_excel_abas()
except Exception as e:
    st.error("Erro ao abrir o arquivo dados.xlsx.")
    st.exception(e)
    st.stop()

# =========================
# PÁGINA INDICADORES WFM TOA
# =========================
if pagina == "Indicadores WFM TOA":

    st.title("📊 Indicadores WFM TOA")

    if ABA_WFM not in abas_disponiveis:
        st.error(f"A aba '{ABA_WFM}' não foi encontrada no arquivo dados.xlsx.")
        st.markdown("### Abas encontradas:")
        st.write(abas_disponiveis)
        st.stop()

    st.markdown(
        """
        <div style='background:#002060;color:white;text-align:center;
                    font-weight:bold;padding:8px;border-radius:4px;
                    font-size:22px;margin-bottom:20px'>
            INDICADORES WFM/TOA
        </div>
        """,
        unsafe_allow_html=True
    )

    indicadores = [
        {
            "titulo": "PREVENTIVAS < 05Min",
            "meta": "0,0%",
            "valores": {
                "SPC": ["6,68%", "6,68%", "0,17%", "0,00%", "0,00%", "0,00%"],
                "SP1": ["24,56%", "24,56%", "0,69%", "0,00%", "0,00%", "0,00%"],
                "SP2": ["0,95%", "0,95%", "0,00%", "0,00%", "0,00%", "0,00%"],
                "SP3": ["0,00%", "0,00%", "0,00%", "0,00%", "0,00%", "0,00%"],
                "SP4": ["1,19%", "1,19%", "0,00%", "0,00%", "0,00%", "0,00%"],
            }
        },
        {
            "titulo": "PREVENTIVAS < 20Min",
            "meta": "0,0%",
            "valores": {
                "SPC": ["6,68%", "6,68%", "0,17%", "0,40%", "0,19%", "0,00%"],
                "SP1": ["24,56%", "24,56%", "0,69%", "1,60%", "0,00%", "0,00%"],
                "SP2": ["0,95%", "0,95%", "0,00%", "0,00%", "0,77%", "0,00%"],
                "SP3": ["0,00%", "0,00%", "0,00%", "0,00%", "0,00%", "0,00%"],
                "SP4": ["1,19%", "1,19%", "0,00%", "0,00%", "0,00%", "0,00%"],
            }
        },
        {
            "titulo": "PREVENTIVAS SEM DESLOCAMENTO",
            "meta": "10,0%",
            "valores": {
                "SPC": ["2,43%", "2,43%", "0,42%", "0,27%", "1,26%", "0,37%"],
                "SP1": ["8,77%", "8,77%", "0,00%", "0,00%", "1,99%", "1,49%"],
                "SP2": ["0,95%", "0,95%", "0,75%", "0,00%", "0,77%", "0,00%"],
                "SP3": ["0,00%", "0,00%", "0,00%", "0,00%", "0,58%", "0,00%"],
                "SP4": ["0,00%", "0,00%", "0,93%", "1,08%", "1,69%", "0,00%"],
            }
        },
        {
            "titulo": "CORRETIVA < 5MIN",
            "meta": "15,0%",
            "valores": {
                "SPC": ["13,41%", "13,41%", "18,82%", "14,09%", "16,88%", "13,24%"],
                "SP1": ["16,02%", "16,02%", "24,72%", "22,95%", "31,10%", "19,68%"],
                "SP2": ["11,73%", "11,73%", "16,15%", "12,34%", "7,49%", "8,81%"],
                "SP3": ["8,37%", "8,37%", "12,77%", "9,71%", "11,86%", "13,32%"],
                "SP4": ["17,53%", "17,53%", "21,64%", "11,35%", "17,09%", "11,16%"],
            }
        },
        {
            "titulo": "CORRETIVA SEM DESLOCAMENTO",
            "meta": "15,0%",
            "valores": {
                "SPC": ["4,28%", "4,28%", "5,95%", "4,37%", "7,61%", "5,96%"],
                "SP1": ["4,49%", "4,49%", "7,92%", "4,55%", "10,64%", "6,76%"],
                "SP2": ["4,51%", "4,51%", "5,54%", "4,97%", "2,50%", "5,07%"],
                "SP3": ["1,16%", "1,16%", "2,79%", "2,52%", "4,17%", "3,81%"],
                "SP4": ["6,98%", "6,98%", "7,56%", "5,44%", "13,13%", "8,20%"],
            }
        },
        {
            "titulo": "ACEITAÇÃO < 5MIN",
            "meta": "0,0%",
            "valores": {
                "SPC": ["7,37%", "7,37%", "3,16%", "0,61%", "1,56%", "0,37%"],
                "SP1": ["8,64%", "8,64%", "0,00%", "0,00%", "1,30%", "0,77%"],
                "SP2": ["2,31%", "2,31%", "9,16%", "0,00%", "0,00%", "0,00%"],
                "SP3": ["4,55%", "4,55%", "1,19%", "0,00%", "1,28%", "0,00%"],
                "SP4": ["14,00%", "14,00%", "2,30%", "2,44%", "3,65%", "0,70%"],
            }
        },
        {
            "titulo": "ATIVIDADE NÃO TÉCNICAS >4H",
            "meta": "5,0%",
            "valores": {
                "SPC": ["7,96%", "7,96%", "4,16%", "6,53%", "1,40%", "4,76%"],
                "SP1": ["7,14%", "7,14%", "7,14%", "14,29%", "2,44%", "3,23%"],
                "SP2": ["4,44%", "4,44%", "5,15%", "4,12%", "1,12%", "5,00%"],
                "SP3": ["16,67%", "16,67%", "2,13%", "7,69%", "0,00%", "10,81%"],
                "SP4": ["3,57%", "3,57%", "2,22%", "0,00%", "2,04%", "0,00%"],
            }
        },
        {
            "titulo": "REFEIÇÃO <55MIN",
            "meta": "0,0%",
            "valores": {
                "SPC": ["0,75%", "0,75%", "0,79%", "0,72%", "0,45%", "0,27%"],
                "SP1": ["0,50%", "0,50%", "1,37%", "1,06%", "0,40%", "0,00%"],
                "SP2": ["2,06%", "2,06%", "0,80%", "0,00%", "1,40%", "1,07%"],
                "SP3": ["0,43%", "0,43%", "0,00%", "0,00%", "0,00%", "0,00%"],
                "SP4": ["0,00%", "0,00%", "0,99%", "1,80%", "0,00%", "0,00%"],
            }
        },
        {
            "titulo": "ACEITAÇÃO REMOTA > 80%",
            "meta": "80,0%",
            "valores": {
                "SPC": ["0,00%", "0,00%", "0,00%", "0,00%", "73,37%", "81,12%"],
                "SP1": ["0,00%", "0,00%", "0,00%", "0,00%", "75,97%", "73,08%"],
                "SP2": ["0,00%", "0,00%", "0,00%", "0,00%", "53,47%", "78,13%"],
                "SP3": ["0,00%", "0,00%", "0,00%", "0,00%", "74,36%", "91,40%"],
                "SP4": ["0,00%", "0,00%", "0,00%", "0,00%", "80,37%", "83,10%"],
            }
        },
    ]

colunas_wfm = st.columns(3)

for i, indicador in enumerate(indicadores):
    with colunas_wfm[i % 3]:
        components.html(
            montar_tabela_indicador(indicador),
            height=260,
            scrolling=False
        )

st.stop()

# =========================
# PÁGINA DASHBOARD TOA
# =========================
st.title("📊 Dashboard TOA")

if ABA_ANALITICO not in abas_disponiveis:
    st.error(f"A aba '{ABA_ANALITICO}' não foi encontrada no arquivo dados.xlsx.")
    st.write(abas_disponiveis)
    st.stop()

try:
    df = carregar_analitico()
except Exception as e:
    st.error("Erro ao carregar a aba ANALÍTICO TOA.")
    st.exception(e)
    st.stop()

# =========================
# MAPEAR COLUNAS
# =========================
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

col_status = get_col_exata("Status") or get_col_contem("Status")
col_tecnico = get_col_exata("Recurso") or get_col_contem("Recurso")

col_area = get_col_exata("Área") or get_col_exata("AREA")

if not col_area:
    col_area = (
        get_col_contem("área")
        or get_col_contem("area")
        or get_col_contem("cidade")
    )

col_atividade = (
    get_col_exata("Tipo de Atividade")
    or get_col_exata("ATIVIDADE")
    or get_col_exata("Atividade")
    or get_col_contem("tipo de atividade")
    or get_col_contem("atividade")
)

# =========================
# FILTROS
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Filtros")

df_f = df.copy()

if col_status:
    opcoes_status = ["Todos"] + sorted(df[col_status].dropna().astype(str).unique())
    status_sel = st.sidebar.selectbox("Status", opcoes_status, index=0)

    if status_sel != "Todos":
        df_f = df_f[df_f[col_status].astype(str) == status_sel]

if col_tecnico:
    opcoes_tecnico = ["Todos"] + sorted(df[col_tecnico].dropna().astype(str).unique())
    tecnico_sel = st.sidebar.selectbox("Técnico", opcoes_tecnico, index=0)

    if tecnico_sel != "Todos":
        df_f = df_f[df_f[col_tecnico].astype(str) == tecnico_sel]

if col_area:
    opcoes_area = ["Todos"] + sorted(df[col_area].dropna().astype(str).unique())
    area_sel = st.sidebar.selectbox("Área", opcoes_area, index=0)

    if area_sel != "Todos":
        df_f = df_f[df_f[col_area].astype(str) == area_sel]

if col_atividade:
    opcoes_atividade = ["Todos"] + sorted(df[col_atividade].dropna().astype(str).unique())
    atividade_sel = st.sidebar.selectbox("Atividade", opcoes_atividade, index=0)

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
else:
    concluidas = 0
    canceladas = 0

taxa_conclusao = (concluidas / total * 100) if total else 0

col1, col2, col3, col4 = st.columns(4)

criar_card(col1, "Total", total, "#1e293b")
criar_card(col2, "Concluídas", concluidas, "#065f46")
criar_card(col3, "Canceladas", canceladas, "#7f1d1d")
criar_card(col4, "% Conclusão", f"{taxa_conclusao:.1f}%", "#1e40af")

st.divider()

# =========================
# GRÁFICOS PRINCIPAIS
# =========================
st.markdown("## 📈 Análise Operacional")

graf1, graf2 = st.columns(2)

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

if col_tecnico:
    with graf2:
        st.subheader("Top Técnicos")

        data_tecnico = (
            df_f[col_tecnico]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
            .sort_values(ascending=True)
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

    df_atividade_area = df_atividade_area[
        df_atividade_area[col_area].isin(top_areas_atividade)
    ]

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
