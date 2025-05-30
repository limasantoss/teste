def limpar_dados(df):
    df_limpo = df.copy()
    for coluna in df_limpo.columns:
        if df_limpo[coluna].isnull().sum() > 0:
            if df_limpo[coluna].dtype in ["float64", "int64"]:
                df_limpo[coluna].fillna(df_limpo[coluna].mean(), inplace=True)
            else:
                moda = df_limpo[coluna].mode()
                if not moda.empty:
                    df_limpo[coluna].fillna(moda[0], inplace=True)
    return df_limpo
