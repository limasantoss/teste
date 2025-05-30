import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def plot_histograma(df, colunas_numericas):
    coluna = st.selectbox("Escolha uma coluna numérica para histograma", colunas_numericas, key='hist')
    fig, ax = plt.subplots()
    sns.histplot(df[coluna], kde=True, ax=ax)
    st.pyplot(fig)

def plot_boxplot(df, colunas_numericas):
    coluna = st.selectbox("Escolha uma coluna para boxplot", colunas_numericas, key='box')
    fig, ax = plt.subplots()
    sns.boxplot(y=df[coluna], ax=ax, color='lightgreen')
    st.pyplot(fig)
    st.info("Pontos fora do retângulo podem ser outliers.")

def plot_frequencia(df, colunas_categoricas):
    coluna = st.selectbox("Escolha uma coluna de texto para gráfico de frequência", colunas_categoricas, key='freq')
    n_max = 20
    vc = df[coluna].value_counts()
    if len(vc) > n_max:
        vc_top = vc.iloc[:n_max]
        outros = vc.iloc[n_max:].sum()
        vc_top['Outros'] = outros
    else:
        vc_top = vc
    fig, ax = plt.subplots()
    vc_top.plot(kind='bar', ax=ax, color='salmon')
    st.pyplot(fig)
    if len(vc) > n_max:
        st.info(f"Exibindo apenas as {n_max} categorias mais frequentes. O restante está agrupado como 'Outros'.")
    if len(vc) > 100:
        st.warning("Coluna com muitos valores únicos (ex: ID). Pode não ser útil para gráficos de frequência.")
