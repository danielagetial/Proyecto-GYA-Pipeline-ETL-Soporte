import yaml
import pandas as pd
import datetime


#Mis librerias - módulos
import src.extract.extract_excel as datos
import src.extract.extract_csv as datos_csv
import src.transform.clean_excel as transform
import src.transform.clean_csv as transform_csv
import src.transform.gold_data as gold
import src.load.load_database as load


def main ():

    with open ("config/config.yaml", "r") as file:
        config = yaml.safe_load(file)

    # Definir la ruta del log
    ruta_log = config['paths']['logs_dir'] + "/logs.txt"

    #EXTRACCIÓN
    with open(ruta_log, "a", encoding="utf-8") as file:
        file.write(f"{datetime.datetime.now()}-INFO:-Iniciando la extracción\n")
    
    df_extraido_encuestas = datos.extraer_datos(config['sources']['encuesta_soporte']['path'])
    df_extraido_jira = datos_csv.extraer_datos(config['sources']['jira']['path'])
    df_extraido_maestro_clientes = datos.extraer_datos(config['sources']['maestro_clientes']['path'])
    #print(df_extraido_encuestas)
    #print(df_extraido_jira)
    #print(df_extraido_maestro_clientes)

    #TRANSFORMACIÓN
    with open(ruta_log, "a", encoding="utf-8") as file:
        file.write(f"{datetime.datetime.now()}-INFO:-Iniciando la transformación\n")

    df_transformado_encuestas = transform.limpiar_datos(df=df_extraido_encuestas,df_maestro=df_extraido_maestro_clientes)
    df_transformado_jira = transform_csv.limpiar_datos_csv(df_extraido_jira)
    #print(df_transformado_encuestas)
    #print(df_transformado_jira)

    df_gold = gold.gold_data(df_transformado_jira, df_transformado_encuestas)
    #print(df_gold)
    #archivo_salida = "RESULTADO_CRUCE.xlsx"
    #df_gold.to_excel(archivo_salida, index=False)

    #CARGA DE DATOS (LOAD)
    with open(ruta_log, "a", encoding="utf-8") as file:
        file.write(f"{datetime.datetime.now()}-INFO:-Iniciando la carga\n")
    
    load.cargar_datos_sql(df_gold)

    # Registro final del proceso
    with open(ruta_log, "a", encoding="utf-8") as file:
        file.write(f"{datetime.datetime.now()}-INFO:-Proceso ETL finalizado con éxito\n")

if __name__ == "__main__":
    main()


