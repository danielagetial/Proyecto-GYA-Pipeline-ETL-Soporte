import pandas as pd

def extraer_datos(ruta:str)->pd.DataFrame:
    print("Empezando a extraer")
    df_extraido_jira = pd.read_csv(ruta, encoding='utf-8')
   

    return df_extraido_jira