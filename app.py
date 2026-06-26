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
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILO
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
# FUNÇÕES GERAIS
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
    except Exception:
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
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: white;
        }}

        .bloco {{
            width: 100%;
            background: white;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            table-layout: fixed;
            font-size: 12px;
            text-align: center;
            border: 2px solid #000;
        }}

        th, td {{
            border: 1px solid #000;
            padding: 3px 4px;
            height: 22px;
            overflow: hidden;
        }}

        .lateral {{
            background: #f4b183;
            width: 110px;
            min-width: 110px;
            max-width: 110px;
            position: relative;
        }}

        .texto-lateral {{
            color: #c00000;
            font-weight: bold;
            font-size: 12px;
            transform: rotate(-45deg);
            white-space: nowrap;
            position: absolute;
            left: 5px;
            top: 68px;
        }}

        .cab-vermelho {{
            background: #c00000;
            color: white;
            font-weight: bold;
        }}

        .mes {{
            background: #0070c0;
            color: white;
            font-weight: bold;
        }}

        .regional {{
            background: #f2f2f2;
            font-weight: bold;
        }}

        .meta {{
            background: white;
            font-weight: bold;
            vertical-align: middle;
        }}

        .titulo-indicador {{
            background: #c00000;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }}
    </style>
    </head>

    <body>
    <div class="bloco">
        <table>
            <tr>
                <th class="lateral" rowspan="8">
                    <div class="texto-lateral">{titulo}</div>
                </th>

                <th class="cab-vermelho" rowspan="3" style="width:95px;">REGIONAL</th>
                <th class="cab-vermelho" rowspan="3" style="width:70px;">META</th>
                <th class="titulo-indicador" colspan="6">{titulo}</th>
            </tr>

            <tr>
                <th class="cab-vermelho" colspan="6">2026</th>
            </tr>

            <tr>
    """

    for mes in meses:
        html += f"<th class='mes'>{mes}</th>"

    html += "</tr>"

    for idx, regional in enumerate(regionais):
        html += "<tr>"
        html += f"<td class='regional'>{regional}</td>"

        if idx == 0:
            html += f"<td class='meta' rowspan='5'>{meta}</td>"

        for valor in valores.get(regional, ["0,00%"] * 6):
            cor = cor_celula(titulo, valor, meta)
            html += f"<td style='background:{cor};'>{valor}</td>"

        html += "</tr>"

    html += """
        </table>
    </div>
    </body>
    </html>
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
        "Indicadores WFM TOA",
        "Validação Indicadores JUN"
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
