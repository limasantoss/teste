import streamlit as st
import pandas as pd
import os
from io import BytesIO
from modulos.eda import mostrar_tipos, mostrar_estatisticas, mostrar_ausentes
from modulos.limpeza import limpar_dados
from modulos.plots import plot_histograma, plot_boxplot, plot_frequencia
import plotly.express as px

st.set_page_config(page_title="Zents EDA", page_icon="zents_logo.png", layout="wide")
st.image("zents_logo.png", width=140)
st.title("Zents EDA ✨")
st.markdown("""
Bem-vindo ao Zents EDA! Siga as etapas abaixo para explorar, limpar e visualizar seus dados.
""")

@st.cache_data
def carregar_arquivo(arquivo, ext):
    if ext.lower() == '.csv':
        return pd.read_csv(arquivo)
    else:
        return pd.read_excel(arquivo)

arquivo = st.file_uploader("Envie seu arquivo CSV ou Excel aqui", type=["csv", "xlsx"])

if arquivo is not None:
    nome_arquivo = arquivo.name
    base, ext = os.path.splitext(nome_arquivo)
    df = carregar_arquivo(arquivo, ext)
    
    st.header("1. Visualização Inicial ✅")
    st.markdown("Veja as primeiras linhas do seu arquivo. Ajuste quantas linhas visualizar.")
    linhas = st.slider("Quantas linhas mostrar?", min_value=5, max_value=min(100, len(df)), value=10)
    st.dataframe(df.head(linhas))

    st.header("2. Tipos de Dados e Estatísticas 📊")
    st.markdown("Veja os tipos das colunas e algumas estatísticas básicas dos seus dados.")
    with st.expander("Ver código desta etapa"):
        st.code("""
mostrar_tipos(df)
mostrar_estatisticas(df)
        """)
    mostrar_tipos(df)
    mostrar_estatisticas(df)

    st.header("3. Valores Ausentes ⚠️")
    st.markdown("Confira quantos valores faltam em cada coluna.")
    with st.expander("Ver código desta etapa"):
        st.code("""
mostrar_ausentes(df)
        """)
    mostrar_ausentes(df)

    st.header("4. Limpeza de Dados 🧹")
    st.markdown("Escolha como tratar os valores ausentes para cada coluna.")
    estrategias = {}
    nulos = df.isnull().sum()
    colunas_nulas = nulos[nulos > 0].index.tolist()
    opcoes_num = ["Preencher com média", "Preencher com mediana", "Preencher com zero", "Remover linhas"]
    opcoes_cat = ["Preencher com moda", "Preencher com 'Desconhecido'", "Remover linhas"]
    for coluna in colunas_nulas:
        st.write(f"Coluna: **{coluna}** ({nulos[coluna]} nulos)")
        if df[coluna].dtype in ["float64", "int64"]:
            estrategias[coluna] = st.selectbox(f"Estratégia para '{coluna}'", opcoes_num, key=coluna)
        else:
            estrategias[coluna] = st.selectbox(f"Estratégia para '{coluna}'", opcoes_cat, key=coluna)

    def limpeza_personalizada(df, estrategias):
        df_limpo = df.copy()
        resumo = []
        for coluna, estrategia in estrategias.items():
            n_antes = df_limpo[coluna].isnull().sum()
            if estrategia == "Preencher com média":
                valor = df_limpo[coluna].mean()
                df_limpo[coluna].fillna(valor, inplace=True)
                resumo.append(f"Coluna {coluna}: {n_antes} preenchidos com média.")
            elif estrategia == "Preencher com mediana":
                valor = df_limpo[coluna].median()
                df_limpo[coluna].fillna(valor, inplace=True)
                resumo.append(f"Coluna {coluna}: {n_antes} preenchidos com mediana.")
            elif estrategia == "Preencher com zero":
                df_limpo[coluna].fillna(0, inplace=True)
                resumo.append(f"Coluna {coluna}: {n_antes} preenchidos com zero.")
            elif estrategia == "Remover linhas":
                df_limpo = df_limpo[df_limpo[coluna].notnull()]
                resumo.append(f"Coluna {coluna}: {n_antes} linhas removidas.")
            elif estrategia == "Preencher com moda":
                valor = df_limpo[coluna].mode()[0]
                df_limpo[coluna].fillna(valor, inplace=True)
                resumo.append(f"Coluna {coluna}: {n_antes} preenchidos com moda.")
            elif estrategia == "Preencher com 'Desconhecido'":
                df_limpo[coluna].fillna("Desconhecido", inplace=True)
                resumo.append(f"Coluna {coluna}: {n_antes} preenchidos com 'Desconhecido'.")
        return df_limpo, resumo

    if st.button("Executar Limpeza de Dados"):
        df_limpo, resumo_limpeza = limpeza_personalizada(df, estrategias)
        st.success("Dados limpos com sucesso! ✅")
        st.markdown("### Relatório da limpeza:")
        for item in resumo_limpeza:
            st.write("- " + item)
        st.markdown(f"Valores ausentes antes: **{nulos.sum()}**<br>Valores ausentes depois: **{df_limpo.isnull().sum().sum()}**", unsafe_allow_html=True)
        st.session_state.df_limpo = df_limpo
        st.session_state.resumo_limpeza = resumo_limpeza
    elif 'df_limpo' not in st.session_state:
        st.session_state.df_limpo = df.copy()
        st.session_state.resumo_limpeza = ["Limpeza padrão executada."]
    
    st.header("5. Visualização de Dados 📈")
    st.markdown("Crie gráficos para explorar seus dados.")
    df_visu = st.session_state.df_limpo
    col_num = df_visu.select_dtypes(include=['number']).columns.tolist()
    col_cat = df_visu.select_dtypes(include=['object', 'category']).columns.tolist()

    # Só carrega cada gráfico ao abrir o subheader (deixa o app leve)
    if col_num:
        with st.expander("Histograma (Interativo)"):
            coluna_hist = st.selectbox("Coluna numérica para histograma", col_num, key='hist_int')
            fig_hist = px.histogram(df_visu, x=coluna_hist)
            st.plotly_chart(fig_hist)
        with st.expander("Boxplot com Outliers"):
            coluna_box = st.selectbox("Coluna para boxplot", col_num, key='box_int')
            fig_box = px.box(df_visu, y=coluna_box, points="all")
            st.plotly_chart(fig_box)
            q1 = df_visu[coluna_box].quantile(0.25)
            q3 = df_visu[coluna_box].quantile(0.75)
            iqr = q3 - q1
            outliers = df_visu[(df_visu[coluna_box] < q1 - 1.5 * iqr) | (df_visu[coluna_box] > q3 + 1.5 * iqr)]
            st.info(f"Foram detectados {len(outliers)} outliers em {coluna_box}. Pontos fora do boxplot são possíveis outliers.")
        with st.expander("Gráfico de Dispersão (Correlação)"):
            col_x = st.selectbox("Eixo X (numérico)", col_num, key='scatter_x')
            col_y = st.selectbox("Eixo Y (numérico)", col_num, key='scatter_y')
            if col_x != col_y:
                fig_scat = px.scatter(df_visu, x=col_x, y=col_y)
                st.plotly_chart(fig_scat)
    if col_cat:
        with st.expander("Gráfico de Frequência (Top N)"):
            coluna_freq = st.selectbox("Coluna categórica", col_cat, key='freq_int')
            n_top = st.slider("Top quantas categorias mostrar?", min_value=3, max_value=30, value=10)
            vc = df_visu[coluna_freq].value_counts()
            vc_top = vc.iloc[:n_top]
            outros = vc.iloc[n_top:].sum()
            if outros > 0:
                vc_top["Outros"] = outros
            fig_freq = px.bar(vc_top, x=vc_top.index, y=vc_top.values, labels={"x":coluna_freq, "y":"Contagem"})
            st.plotly_chart(fig_freq)
            st.info(f"Exibindo as {n_top} categorias mais frequentes. O restante está agrupado como 'Outros'.")

    st.header("6. Arquivo Tratado e Relatórios 📥")
    st.markdown("Baixe seu arquivo limpo ou um relatório completo.")
    df_out = st.session_state.df_limpo
    if ext.lower() == ".csv":
        csv = df_out.to_csv(index=False).encode('utf-8')
        st.download_button("Baixar CSV Limpo", data=csv, file_name=nome_arquivo, mime="text/csv")
    else:
        saida = BytesIO()
        with pd.ExcelWriter(saida, engine='openpyxl') as writer:
            df_out.to_excel(writer, index=False)
        st.download_button("Baixar Excel Limpo", data=saida.getvalue(), file_name=nome_arquivo, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Relatório PDF em memória
    from fpdf import FPDF

    def gerar_pdf_mem(df, resumo_limpeza):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Relatório Zents EDA", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Total de linhas: {len(df)}", 0, 1)
        pdf.cell(0, 10, f"Total de colunas: {len(df.columns)}", 0, 1)
        pdf.cell(0, 10, "Resumo da Limpeza:", 0, 1)
        for item in resumo_limpeza:
            pdf.cell(0, 10, item, 0, 1)
        pdf.cell(0, 10, "Tipos de Dados:", 0, 1)
        for col in df.dtypes.index:
            pdf.cell(0, 10, f"{col}: {df.dtypes[col]}", 0, 1)
        pdf_bytes = BytesIO()
        pdf.output(pdf_bytes)
        pdf_bytes.seek(0)
        return pdf_bytes

    if st.button("Baixar Relatório PDF (resumo)"):
        resumo = st.session_state.resumo_limpeza if 'resumo_limpeza' in st.session_state else ["Limpeza padrão executada."]
        pdf_bytes = gerar_pdf_mem(df_out, resumo)
        st.download_button("Baixar PDF", data=pdf_bytes, file_name="relatorio_eda.pdf", mime="application/pdf")

    # Download do código da limpeza
    codigo_limpeza = """import pandas as pd\n\n# Substitua pelo seu arquivo\ndf = pd.read_csv('seuarquivo.csv')\n\n# Limpeza realizada:\n"""
    for coluna, estrategia in estrategias.items():
        if estrategia == "Preencher com média":
            codigo_limpeza += f"df['{coluna}'] = df['{coluna}'].fillna(df['{coluna}'].mean())\n"
        elif estrategia == "Preencher com mediana":
            codigo_limpeza += f"df['{coluna}'] = df['{coluna}'].fillna(df['{coluna}'].median())\n"
        elif estrategia == "Preencher com zero":
            codigo_limpeza += f"df['{coluna}'] = df['{coluna}'].fillna(0)\n"
        elif estrategia == "Remover linhas":
            codigo_limpeza += f"df = df[df['{coluna}'].notnull()]\n"
        elif estrategia == "Preencher com moda":
            codigo_limpeza += f"df['{coluna}'] = df['{coluna}'].fillna(df['{coluna}'].mode()[0])\n"
        elif estrategia == "Preencher com 'Desconhecido'":
            codigo_limpeza += f"df['{coluna}'] = df['{coluna}'].fillna('Desconhecido')\n"
    codigo_limpeza += "\ndf.to_csv('seuarquivo_limpo.csv', index=False)\n"
    st.download_button("Baixar código Python da limpeza", data=codigo_limpeza, file_name="codigo_limpeza.py", mime="text/x-python")
else:
    st.info("Envie seu arquivo para começar!")
