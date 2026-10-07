import os
import urllib
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Para cargar las variables de entorno del archivo .env
load_dotenv()

# Se recibe el dataframe a guardar en SQL Server y el nombre que tendra la tabla en la base de datos
def cargar_datos_sql(
    df: pd.DataFrame, nombre_tabla: str = "DATOS_SOPORTE"
):
    # Guardar en la carpeta gold
    df.to_csv("data\\gold\\gold.csv", index=False)
    df.to_json("data\\gold\\gold.json", orient="records")
    print("Archivos guardados en la carpeta Gold exitosamente.")

    # Se define el servidor y la base de datos destino
    SERVER_NAME = os.getenv("SERVER_NAME")
    DATABASE_NAME = os.getenv("DATABASE_NAME")

    # Construcción de la cadena de conexión (Autenticación de Windows para ingresar a la bd)
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER_NAME};"
        f"DATABASE={DATABASE_NAME};"
        f"Trusted_Connection=yes;"
    )

    # Crear el motor de conexión de SQLAlchemy
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    print(f"Cargando datos en la tabla [{nombre_tabla}] de SQL Server...")

    # Carga del dataframe recibido a la base de datos
    df.to_sql(
        name=nombre_tabla,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=1000,
    )

    print(
        "¡Carga completada exitosamente! Los datos ya están disponibles en SQL Server."
    )