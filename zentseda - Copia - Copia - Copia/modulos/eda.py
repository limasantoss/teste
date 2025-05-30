def mostrar_tipos(df):
    import streamlit as st
    st.write("Tipos de Dados:")
    st.write(df.dtypes)

def mostrar_estatisticas(df):
    import streamlit as st
    st.write("Estatísticas Básicas:")
    st.write(df.describe())

def mostrar_ausentes(df):
    import streamlit as st
    ausentes = df.isnull().sum()
    st.write(ausentes)
    if ausentes.sum() > 0:
        st.warning("Seu arquivo tem dados faltando!")
    else:
        st.success("Sem dados faltando! Ótimo!")
