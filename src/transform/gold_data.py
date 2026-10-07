import pandas as pd


def gold_data(df_jira: pd.DataFrame, df_encuestas: pd.DataFrame) -> pd.DataFrame:
    #Unir los datos de jira y encuestas

    df_integrado = df_jira.merge(df_encuestas, on='ID_Ticket', how='left')
    return df_integrado