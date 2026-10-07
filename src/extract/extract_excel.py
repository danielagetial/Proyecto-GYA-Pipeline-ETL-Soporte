import pandas as pd



def extraer_datos(ruta:str)->pd.DataFrame:
    print("Empezando a extraer")
    df = pd.read_excel(ruta)
   

    return df