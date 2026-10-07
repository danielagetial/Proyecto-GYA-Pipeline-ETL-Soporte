import pandas as pd
import yaml #Se importa yaml y os para enviar el dataframe limpio a Silver
import os

def limpiar_datos_csv(df: pd.DataFrame) -> pd.DataFrame:
    print("Empezando a limpiar los datos...")

    #Cambio nombre de columna Clave de incidencia a ID_Ticket
    #Este cambio se realiza ya que esta columna será la llave para unir ambas tablas (Jira y encuestas soporte)
    if "Clave de incidencia" in df.columns:
        df = df.rename(columns={"Clave de incidencia": "ID_Ticket"})

    #Diccionario de columnas: estas son las columnas de interes para la visualización final.
    columnas_utiles = [
        "ID_Ticket",
        "Tipo de Incidencia",
        "ID de la incidencia",
        "Resumen",
        "Etiquetas",
        "Clave del proyecto",
        "Nombre del proyecto",
        "Campo personalizado (Organizations)",
        "Persona asignada",
        "Estado",
        "Prioridad",
        "Creada",
        "Fecha de vencimiento",
        "Campo personalizado (Actual start).1",
        "Campo personalizado (Actual end).1",
        "Campo personalizado (Razón)"
    ]

    # Filtrar columnas
    cols_presentes = [col for col in columnas_utiles if col in df.columns]
    df = df[cols_presentes]

    # Dejar solo el primer nombre del agente:
    df["Persona asignada"] = df["Persona asignada"].astype(str).str.strip().str.split().str[0]

    # --- ENVIAR A SILVER-----
    # Se carga la configuración del yaml
    with open ("config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    
    # Se construye la ruta uniendo el directorio silver + nombre archivo limpio
    directorio_silver = config["paths"]["silver_dir"]
    ruta_salida = os.path.join(directorio_silver, "Jira_cleaned.csv")
    
    # Guardar el archivo en data/silver
    df.to_csv(ruta_salida, index=False)

    return df