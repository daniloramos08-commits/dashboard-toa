import pandas as pd
import streamlit as st
import plotly.express as px
import unicodedata
import streamlit.components.v1 as components

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="Dashboard TOA",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .main { background-color: #ffffff; }
        h1, h2, h3 { font-weight: 800; }
        section[data-testid="stSidebar"] { background-color: #f1f5f9; }
    </style>
    """,
    unsafe_allow_html=True
)

ARQUIVO = "dados.xlsx"
ABA_ANALITICO = "ANALÍTICO TOA"
ABA_WFM = "INDICADORES WFM TOA"

TECNICOS_NOTURNO_AREA = {
    "ricardo de araujo santos": "SP1",
    "rafael lopes vieira": "SP3",
    "renato monteiro soares": "SP4"
}

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


def encontrar_coluna_por_nome(df_base, nome_exato=None, contem=None):
    colunas = list(df_base.columns)

    if nome_exato:
        alvo = normalizar_texto(nome_exato)
        for col in colunas:
            if normalizar_texto(col) == alvo:
                return col

    if contem:
        alvo = normalizar_texto(contem)
        for col in colunas:
            if alvo in normalizar_texto(col):
                return col

    return None


def formatar_percentual(valor):
    try:
        return f"{valor * 100:.2f}%".replace(".", ",")
    except Exception:
        return "0,00%"


def valor_para_float(valor):
    try:
        return float(str(valor).replace("%", "").replace(",", "."))
    except Exception:
        return 0


def cor_celula(titulo, valor, meta):
    v = valor_para_float(valor)
    m = valor_para_float(meta)

    titulo_norm = normalizar_texto(titulo)

    if "aceitacao remota" in titulo_norm:
        return "#c6efce" if v >= m else "#ffc7ce"

    return "#c6efce" if v <= m else "#ffc7ce"


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


def normalizar_area(valor, recurso=None):
    area = str(valor).strip().upper()
    recurso_norm = normalizar_texto(recurso) if recurso is not None else ""

    # Regra especial: técnicos do noturno entram na área real
    if "NOTURNO" in area:
        return TECNICOS_NOTURNO_AREA.get(recurso_norm, "NOTURNO")

    # Padronização das áreas
    if "SPC1" in area or "SP1" in area:
        return "SP1"

    if "SPC2" in area or "SP2" in area:
        return "SP2"

    if "SPC3" in area or "SP3" in area:
        return "SP3"

    if "SPC4" in area or "SP4" in area:
        return "SP4"

    return area


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
# CARREGAR ARQUIVO
# =========================
try:
    abas_disponiveis = carregar_excel_abas()
except Exception as e:
    st.error("Erro ao abrir o arquivo dados.xlsx.")
    st.exception(e)
    st.stop()

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
# CÁLCULO WFM JUN
# =========================

def preparar_base_jun(df_base):
    df_calc = df_base.copy()
    df_calc.columns = df_calc.columns.str.strip()

    col_mes = (
        encontrar_coluna_por_nome(df_calc, nome_exato="MÊS")
        or encontrar_coluna_por_nome(df_calc, contem="mes")
    )

    col_area = (
        encontrar_coluna_por_nome(df_calc, nome_exato="ÁREA")
        or encontrar_coluna_por_nome(df_calc, contem="area")
    )

    col_tipo = (
        encontrar_coluna_por_nome(df_calc, nome_exato="Tipo de Atividade")
        or encontrar_coluna_por_nome(df_calc, contem="atividade")
    )

    col_status = (
        encontrar_coluna_por_nome(df_calc, nome_exato="Status")
        or encontrar_coluna_por_nome(df_calc, contem="status")
    )

    col_recurso = (
        encontrar_coluna_por_nome(df_calc, nome_exato="Recurso")
        or encontrar_coluna_por_nome(df_calc, contem="recurso")
    )

    if not col_mes or not col_area or not col_tipo or not col_status or not col_recurso:
        st.error("Não foi possível localizar colunas obrigatórias: MÊS, ÁREA, Tipo de Atividade, Status ou Recurso.")
        st.write("Colunas encontradas:", list(df_calc.columns))
        st.stop()

    df_calc["_MES"] = pd.to_numeric(df_calc[col_mes], errors="coerce")
    df_calc["_RECURSO"] = df_calc[col_recurso].astype(str).str.strip()
    df_calc["_TIPO"] = df_calc[col_tipo].astype(str).str.strip()
    df_calc["_STATUS"] = df_calc[col_status].astype(str).str.strip()
    df_calc["_STATUS_NORM"] = df_calc["_STATUS"].apply(normalizar_texto)

    # Aqui está a correção do NOTURNO:
    # se a área for NOTURNO, usa o nome do técnico para jogar na área correta.
    df_calc["_AREA_PADRAO"] = df_calc.apply(
        lambda linha: normalizar_area(linha[col_area], linha["_RECURSO"]),
        axis=1
    )

    df_calc = df_calc[
        (df_calc["_MES"] == 6) &
        (df_calc["_AREA_PADRAO"].isin(["SP1", "SP2", "SP3", "SP4"]))
    ]

    # Regra WFM: considerar Concluída e Não Concluída
    df_calc = df_calc[
        df_calc["_STATUS_NORM"].isin(["concluida", "nao concluida"])
    ]

    return df_calc

def calcular_percentual_flag(df_base, area, tipos_atividade, coluna_flag):
    base = df_base[
        (df_base["_AREA_PADRAO"] == area) &
        (df_base["_TIPO"].isin(tipos_atividade))
    ]

    total = len(base)

    if total == 0 or not coluna_flag:
        return 0

    numerador = pd.to_numeric(base[coluna_flag], errors="coerce").fillna(0).sum()

    return numerador / total


def calcular_percentual_nao_tecnico(df_base, area, coluna_nao_tec, coluna_flag_4h):
    base = df_base[df_base["_AREA_PADRAO"] == area]

    if not coluna_nao_tec or not coluna_flag_4h:
        return 0

    base = base[
        base[coluna_nao_tec].astype(str).str.strip().str.upper() != "TECNICA"
    ]

    total = len(base)

    if total == 0:
        return 0

    numerador = pd.to_numeric(base[coluna_flag_4h], errors="coerce").fillna(0).sum()

    return numerador / total


def calcular_aceitacao_remota(df_base, area, col_remota):
    base = df_base[
        (df_base["_AREA_PADRAO"] == area) &
        (df_base["_TIPO"] == "M Aceitação")
    ]

    total = len(base)

    if total == 0 or not col_remota:
        return 0, 0, 0

    sim = base[col_remota].astype(str).str.strip().str.upper().isin(["SIM", "S"]).sum()

    return sim / total, sim, total


def calcular_spc_media(resultados_area):
    valores = [
        resultados_area.get("SP1", 0),
        resultados_area.get("SP2", 0),
        resultados_area.get("SP3", 0),
        resultados_area.get("SP4", 0)
    ]

    return sum(valores) / len(valores)


def gerar_validacao_indicadores_jun(df_base):
    df_jun = preparar_base_jun(df_base)

    col_prev_5 = encontrar_coluna_por_nome(df_jun, nome_exato="Preventiva <00:05:00")
    col_20 = encontrar_coluna_por_nome(df_jun, nome_exato="<00:20:00")
    col_55 = encontrar_coluna_por_nome(df_jun, nome_exato="<00:55:00")
    col_aceit_5 = encontrar_coluna_por_nome(df_jun, nome_exato="Aceitação <00:05:00")

    col_sem_desloc = (
        encontrar_coluna_por_nome(df_jun, nome_exato="00:00:00")
        or encontrar_coluna_por_nome(df_jun, contem="deslocamento")
    )

    col_4h = (
        encontrar_coluna_por_nome(df_jun, nome_exato=">04:00:00")
        or encontrar_coluna_por_nome(df_jun, contem="04:00")
    )

    col_nao_tec = (
        encontrar_coluna_por_nome(df_jun, nome_exato="NÃO TEC")
        or encontrar_coluna_por_nome(df_jun, contem="nao tec")
    )

    col_remota = (
        encontrar_coluna_por_nome(df_jun, nome_exato="Remota?")
        or encontrar_coluna_por_nome(df_jun, contem="remota")
    )

    areas = ["SP1", "SP2", "SP3", "SP4"]

    definicoes = [
        {
            "indicador": "PREVENTIVAS < 05Min",
            "meta": "0,0%",
            "tipo": "flag",
            "atividades": ["M Preventiva"],
            "flag": col_prev_5
        },
        {
            "indicador": "PREVENTIVAS < 20Min",
            "meta": "0,0%",
            "tipo": "flag",
            "atividades": ["M Preventiva"],
            "flag": col_20
        },
        {
            "indicador": "PREVENTIVAS SEM DESLOCAMENTO",
            "meta": "10,0%",
            "tipo": "flag",
            "atividades": ["M Preventiva"],
            "flag": col_sem_desloc
        },
        {
            "indicador": "CORRETIVA < 5MIN",
            "meta": "15,0%",
            "tipo": "flag",
            "atividades": ["M Corretiva", "M Corretiva Emergencial"],
            "flag": col_aceit_5
        },
        {
            "indicador": "CORRETIVA SEM DESLOCAMENTO",
            "meta": "15,0%",
            "tipo": "flag",
            "atividades": ["M Corretiva", "M Corretiva Emergencial"],
            "flag": col_sem_desloc
        },
        {
            "indicador": "ACEITAÇÃO < 5MIN",
            "meta": "0,0%",
            "tipo": "flag",
            "atividades": ["M Aceitação"],
            "flag": col_aceit_5
        },
        {
            "indicador": "ATIVIDADE NÃO TÉCNICAS >4H",
            "meta": "5,0%",
            "tipo": "nao_tecnica",
            "flag": col_4h
        },
        {
            "indicador": "REFEIÇÃO <55MIN",
            "meta": "0,0%",
            "tipo": "flag",
            "atividades": ["Refeição", "MV Refeição"],
            "flag": col_55
        },
        {
            "indicador": "ACEITAÇÃO REMOTA > 80%",
            "meta": "80,0%",
            "tipo": "remota"
        }
    ]

    linhas = []

    for definicao in definicoes:
        indicador = definicao["indicador"]
        meta = definicao["meta"]
        tipo = definicao["tipo"]

        resultados_area = {}
        soma_sim_remota = 0
        soma_total_remota = 0
        linhas_indicador = []

        for area in areas:
            if tipo == "flag":
                valor = calcular_percentual_flag(
                    df_jun,
                    area,
                    definicao["atividades"],
                    definicao["flag"]
                )

            elif tipo == "nao_tecnica":
                valor = calcular_percentual_nao_tecnico(
                    df_jun,
                    area,
                    col_nao_tec,
                    definicao["flag"]
                )

            elif tipo == "remota":
                valor, sim, total = calcular_aceitacao_remota(
                    df_jun,
                    area,
                    col_remota
                )

                soma_sim_remota += sim
                soma_total_remota += total

            else:
                valor = 0

            resultados_area[area] = valor

            linhas_indicador.append({
                "Indicador": indicador,
                "Área": area,
                "Meta": meta,
                "JUN Calculado": formatar_percentual(valor)
            })

        if tipo == "remota":
            spc = soma_sim_remota / soma_total_remota if soma_total_remota else 0
        else:
            spc = calcular_spc_media(resultados_area)

        linhas.append({
            "Indicador": indicador,
            "Área": "SPC",
            "Meta": meta,
            "JUN Calculado": formatar_percentual(spc)
        })

        linhas.extend(linhas_indicador)

    return pd.DataFrame(linhas)


# =========================
# HISTÓRICO WFM JAN-MAI
# =========================
HISTORICO_WFM = {
    "PREVENTIVAS < 05Min": {
        "SPC": ["6,68%", "6,68%", "0,17%", "0,00%", "0,00%"],
        "SP1": ["24,56%", "24,56%", "0,69%", "0,00%", "0,00%"],
        "SP2": ["0,95%", "0,95%", "0,00%", "0,00%", "0,00%"],
        "SP3": ["0,00%", "0,00%", "0,00%", "0,00%", "0,00%"],
        "SP4": ["1,19%", "1,19%", "0,00%", "0,00%", "0,00%"],
    },
    "PREVENTIVAS < 20Min": {
        "SPC": ["6,68%", "6,68%", "0,17%", "0,40%", "0,19%"],
        "SP1": ["24,56%", "24,56%", "0,69%", "1,60%", "0,00%"],
        "SP2": ["0,95%", "0,95%", "0,00%", "0,00%", "0,77%"],
        "SP3": ["0,00%", "0,00%", "0,00%", "0,00%", "0,00%"],
        "SP4": ["1,19%", "1,19%", "0,00%", "0,00%", "0,00%"],
    },
    "PREVENTIVAS SEM DESLOCAMENTO": {
        "SPC": ["2,43%", "2,43%", "0,42%", "0,27%", "1,26%"],
        "SP1": ["8,77%", "8,77%", "0,00%", "0,00%", "1,99%"],
        "SP2": ["0,95%", "0,95%", "0,75%", "0,00%", "0,77%"],
        "SP3": ["0,00%", "0,00%", "0,00%", "0,00%", "0,58%"],
        "SP4": ["0,00%", "0,00%", "0,93%", "1,08%", "1,69%"],
    },
    "CORRETIVA < 5MIN": {
        "SPC": ["13,41%", "13,41%", "18,82%", "14,09%", "16,88%"],
        "SP1": ["16,02%", "16,02%", "24,72%", "22,95%", "31,10%"],
        "SP2": ["11,73%", "11,73%", "16,15%", "12,34%", "7,49%"],
        "SP3": ["8,37%", "8,37%", "12,77%", "9,71%", "11,86%"],
        "SP4": ["17,53%", "17,53%", "21,64%", "11,35%", "17,09%"],
    },
    "CORRETIVA SEM DESLOCAMENTO": {
        "SPC": ["4,28%", "4,28%", "5,95%", "4,37%", "7,61%"],
        "SP1": ["4,49%", "4,49%", "7,92%", "4,55%", "10,64%"],
        "SP2": ["4,51%", "4,51%", "5,54%", "4,97%", "2,50%"],
        "SP3": ["1,16%", "1,16%", "2,79%", "2,52%", "4,17%"],
        "SP4": ["6,98%", "6,98%", "7,56%", "5,44%", "13,13%"],
    },
    "ACEITAÇÃO < 5MIN": {
        "SPC": ["7,37%", "7,37%", "3,16%", "0,61%", "1,56%"],
        "SP1": ["8,64%", "8,64%", "0,00%", "0,00%", "1,30%"],
        "SP2": ["2,31%", "2,31%", "9,16%", "0,00%", "0,00%"],
        "SP3": ["4,55%", "4,55%", "1,19%", "0,00%", "1,28%"],
        "SP4": ["14,00%", "14,00%", "2,30%", "2,44%", "3,65%"],
    },
    "ATIVIDADE NÃO TÉCNICAS >4H": {
        "SPC": ["7,96%", "7,96%", "4,16%", "6,53%", "1,40%"],
        "SP1": ["7,14%", "7,14%", "7,14%", "14,29%", "2,44%"],
        "SP2": ["4,44%", "4,44%", "5,15%", "4,12%", "1,12%"],
        "SP3": ["16,67%", "16,67%", "2,13%", "7,69%", "0,00%"],
        "SP4": ["3,57%", "3,57%", "2,22%", "0,00%", "2,04%"],
    },
    "REFEIÇÃO <55MIN": {
        "SPC": ["0,75%", "0,75%", "0,79%", "0,72%", "0,45%"],
        "SP1": ["0,50%", "0,50%", "1,37%", "1,06%", "0,40%"],
        "SP2": ["2,06%", "2,06%", "0,80%", "0,00%", "1,40%"],
        "SP3": ["0,43%", "0,43%", "0,00%", "0,00%", "0,00%"],
        "SP4": ["0,00%", "0,00%", "0,99%", "1,80%", "0,00%"],
    },
    "ACEITAÇÃO REMOTA > 80%": {
        "SPC": ["0,00%", "0,00%", "0,00%", "0,00%", "73,37%"],
        "SP1": ["0,00%", "0,00%", "0,00%", "0,00%", "75,97%"],
        "SP2": ["0,00%", "0,00%", "0,00%", "0,00%", "53,47%"],
        "SP3": ["0,00%", "0,00%", "0,00%", "0,00%", "74,36%"],
        "SP4": ["0,00%", "0,00%", "0,00%", "0,00%", "80,37%"],
    },
}

METAS_WFM = {
    "PREVENTIVAS < 05Min": "0,0%",
    "PREVENTIVAS < 20Min": "0,0%",
    "PREVENTIVAS SEM DESLOCAMENTO": "10,0%",
    "CORRETIVA < 5MIN": "15,0%",
    "CORRETIVA SEM DESLOCAMENTO": "15,0%",
    "ACEITAÇÃO < 5MIN": "0,0%",
    "ATIVIDADE NÃO TÉCNICAS >4H": "5,0%",
    "REFEIÇÃO <55MIN": "0,0%",
    "ACEITAÇÃO REMOTA > 80%": "80,0%",
}


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
            padding: 4px 4px;
            height: 24px;
            overflow: hidden;
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
            font-size: 13px;
        }}
    </style>
    </head>

    <body>
        <table>
            <tr>
                <th class="cab-vermelho" rowspan="3">REGIONAL</th>
                <th class="cab-vermelho" rowspan="3">META</th>
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
    </body>
    </html>
    """

    return html


# =========================
# PÁGINA WFM
# =========================
if pagina == "Indicadores WFM TOA":

    st.title("📊 Indicadores WFM TOA")

    df_validacao = gerar_validacao_indicadores_jun(df)
    jun_lookup = {
        (row["Indicador"], row["Área"]): row["JUN Calculado"]
        for _, row in df_validacao.iterrows()
    }

    indicadores_wfm = []

    for indicador, valores_hist in HISTORICO_WFM.items():
        valores_com_jun = {}

        for area in ["SPC", "SP1", "SP2", "SP3", "SP4"]:
            historico = valores_hist.get(area, ["0,00%"] * 5)
            jun = jun_lookup.get((indicador, area), "0,00%")
            valores_com_jun[area] = historico + [jun]

        indicadores_wfm.append({
            "titulo": indicador,
            "meta": METAS_WFM.get(indicador, "0,0%"),
            "valores": valores_com_jun
        })

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

    colunas_wfm = st.columns(2)

    for i, indicador in enumerate(indicadores_wfm):
        with colunas_wfm[i % 2]:
            components.html(
                montar_tabela_indicador(indicador),
                height=310,
                scrolling=False
            )

    st.stop()

    df_validacao = gerar_validacao_indicadores_jun(df)
    
# =========================
# DASHBOARD TOA
# =========================
st.title("📊 Dashboard TOA")

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
    col_area = get_col_contem("area") or get_col_contem("cidade")

col_atividade = (
    get_col_exata("Tipo de Atividade")
    or get_col_exata("ATIVIDADE")
    or get_col_exata("Atividade")
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
# CARDS
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
# GRÁFICOS
# =========================
with st.expander("📈 Análise Operacional", expanded=True):

    graf1, graf2 = st.columns(2)

    if col_status:
        with graf1:
            st.subheader("Status das Atividades")

            data_status = df_f[col_status].dropna().astype(str).value_counts().reset_index()
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

            st.plotly_chart(fig_status, use_container_width=True, key="grafico_status")

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

            st.plotly_chart(fig_tecnico, use_container_width=True, key="grafico_tecnico")

st.divider()

# =========================
# STATUS POR ÁREA
# =========================
if col_status and col_area:
    st.markdown("## 📊 Status por Área")

    df_area_status = df_f.groupby([col_area, col_status]).size().reset_index(name="Quantidade")

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

    st.plotly_chart(fig_area, use_container_width=True, key="grafico_status_area")

st.divider()

# =========================
# ATIVIDADES POR ÁREA
# =========================
if col_atividade and col_area:
    st.markdown("## 📌 Atividades por Área")

    df_atividade_area = df_f.groupby([col_area, col_atividade]).size().reset_index(name="Quantidade")

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

    st.plotly_chart(fig_atividade_area, use_container_width=True, key="grafico_atividade_area")

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
