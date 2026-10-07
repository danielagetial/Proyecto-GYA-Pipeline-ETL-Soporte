import re
import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process
import yaml #Se importa yaml y os para enviar el dataframe limpio a Silver
import os 


def limpiar_datos(df: pd.DataFrame, df_maestro: pd.DataFrame) -> pd.DataFrame:
    print("Empezando a limpiar los datos...")

    #Cambio nombre de columna para facilitar el código
    if "Nombre de la Compañía" in df.columns:
        df = df.rename(columns={"Nombre de la Compañía": "NOMBRE_COMPANIA"})

    # --- FUNCIÓN DE LIMPIEZA ---
    def limpiar_texto(texto):
        if pd.isna(texto):   # Si el valor es nulo, devuelve un texto vacío
            return ""
        txt = str(texto).upper().strip() #Convierte el texto a mayúscula y elimina espacios innecesarios

        # Quitamos tildes para que, por ejemplo, 'QUINDIO' y 'QUÍNDIO' sean idénticos
        replacements = (
            ("Á", "A"),
            ("É", "E"),
            ("Í", "I"),
            ("Ó", "O"),
            ("Ú", "U"),
        )
        for a, b in replacements:
            txt = txt.replace(a, b)

        # Quitamos puntos, comas, caracteres especiales y múltiples espacios seguidos usando expresiones regulares
        txt = re.sub(r"[.,\-_/]", " ", txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        return txt

    # Aplicamos la limpieza a las columnas NOMBRE_COMPANIA y CLIENTE de df_encuesta y df_maestro
    if "NOMBRE_COMPANIA" in df.columns:
        df["NOMBRE_COMPANIA_LIMPIO"] = df["NOMBRE_COMPANIA"].apply(
            limpiar_texto
        )

    df_maestro["CLIENTE_LIMPIO"] = df_maestro["CLIENTE"].apply(limpiar_texto)

    # Mapeo para recuperar el formato exacto del maestro al final (se crea un diccionario con el nombre original y el nombre limpio)
    mapeo_original = pd.Series(
        df_maestro["CLIENTE"].values, index=df_maestro["CLIENTE_LIMPIO"]
    ).to_dict()

    #Función de búsqueda de clientes: 
    #Aquí se realiza el match entre el nombre ingresado en la encuesta y la lista oficial de clientes en el archivo maestro
    def buscar_cliente_maestro(nombre_encuesta, opciones_maestro):
        if not nombre_encuesta or nombre_encuesta == "":  #Si el campo llega vacio retonar None
            return None, None
        #Filtra el maestro eliminando valores nulos o vacíos y extrae una lista de nombres de empresas únicos.
        lista_opciones = (
            opciones_maestro.replace("", None).dropna().unique().tolist()
        )
        #Si no hay empresas para comparar, retorna "SIN COINCIDENCIA SEGURA", None.
        if not lista_opciones:
            return "SIN COINCIDENCIA SEGURA", None

        #Usamos token_set_ratio de RapidFuzz para encontrar la empresa del maestro más parecida
        #token_set_ratio ignora el orden de las palabras e ignora palabras repetidas (se busca un 100% de similitud de "CAFÉ QUINDÍO" con "CAFÉ QUINDÍO S.A.S.")
        resultado = process.extractOne(
            str(nombre_encuesta), lista_opciones, scorer=fuzz.token_set_ratio
        )

        if resultado:
            mejor_coincidencia, puntaje, _ = resultado

            # --- VALIDACIÓN ADICIONAL DE SEGURIDAD (Control de falsos positivos) ---
            # Si el puntaje es alto por palabras comunes como "COLOMBIA", se hace un segundo filtro.
            # Quitamos palabras corporativas de control SOLO para verificar falsos positivos
            # como Grupo Luz y Fuerza Colombia vs Sero Colombia (estos dos nombres los estaba relacionando anteriormente)
            palabras_ruido = (
                r"\b(S\.?A\.?S\.?|S\.?A\.?|LTDA\.?|LTD\.?|GRUPOS?|COLOMBIA)\b"
            )
            txt1_check = re.sub(palabras_ruido, "", nombre_encuesta).strip()
            txt2_check = re.sub(
                palabras_ruido, "", mejor_coincidencia
            ).strip()

            # Si al quitar el ruido la palabra principal no tiene NADA en común (como Grupo Luz y Fuerza vs Sero)
            # el token_set_ratio de control caerá drásticamente.
            puntaje_control = fuzz.token_set_ratio(txt1_check, txt2_check)

            # Regla de aceptación:
            # Se acepta si el puntaje original es mayor o igual al 85%  y el puntaje de control es de mayor o igual al 60%
            # y se rechaza si el puntaje de control cae por debajo de 60% (como Luz y Fuerza vs Sero)
            if puntaje >= 85 and puntaje_control >= 60:
                return mapeo_original.get(mejor_coincidencia), round(
                    puntaje, 2
                )

        return "SIN COINCIDENCIA SEGURA", None

    # Ejecución del proceso:
    # Se aplica la función buscar_cliente_maestro fila por fila a la columna NOMBRE_COMPANIA_LIMPIO de la encuesta_soporte
    # lambda es una función rápida para pasarle a la función buscar_cliente_maestro el nombre de cada empresa (para cada celda x de esa columna)
    print("Aplicando función buscar_cliente_maestro")

    if "NOMBRE_COMPANIA_LIMPIO" in df.columns:
        resultados = df["NOMBRE_COMPANIA_LIMPIO"].apply(
            lambda x: pd.Series(
                buscar_cliente_maestro(x, df_maestro["CLIENTE_LIMPIO"])
            )
        )

        df[["CLIENTE_MAESTRO_ENCONTRADO", "PORCENTAJE_CERTEZA"]] = resultados

        # Limpiar columna temporal antes de guardar
        df = df.drop(columns=["NOMBRE_COMPANIA_LIMPIO"])

    #LIMPIEZA DE TICKETS
    # Validar y corregir formato de la columna ticket
    if "Número de Ticket" in df.columns:

        def formatear_ticket(val):
            # Manejo de nulos: Si el valor es nulo
            if pd.isna(val):
                return np.nan

            val_str = str(val).strip().upper()

            # Si contiene textos equivalentes a vacío
            if val_str in ["NAN", "NAT", "<NA>", ""]:
                return np.nan

            # Quitar decimales flotantes (ej. 123.0 -> 123)
            if val_str.endswith(".0"):
                val_str = val_str[:-2]

            # CASO 1 LIMPIEZA TICKETS: Formato estricto LETRAS-NÚMEROS (ej. ALMGR-10 REPORTES, GLF1-58)
            # Busca un prefijo de letras (con números opcionales intermedios como GLF1) y luego el bloque numérico final
            match_prefijo = re.search(r"\b([A-Z]+[0-9]*)-?([0-9]+)\b", val_str)

            if match_prefijo:
                letras = match_prefijo.group(1)
                numeros = match_prefijo.group(2)

                # REGLA: Si el número tiene más de 4 dígitos, es inválido. Los números de un id ticket no superan los 4 digitos.
                if len(numeros) > 4:
                    return np.nan

                # Si la palabra inicial es genérica (como TICKET), se reemplaza por el prefijo temporal NAN (NAN-número)
                if letras in ["TICKET", "TICKETS", "N", "NO", "NUMERO"]:
                    return f"NAN-{numeros}"

                return f"{letras}-{numeros}"

            # CASO 2 LIMPIEZA TICKETS: Solo números o palabras genéricas con números sueltos (ej. 123, "TICKET 123")
            # Para este caso se extrae todos los bloques numéricos del string
            bloques_numericos = re.findall(r"\d+", val_str)

            if bloques_numericos:
                # Tomamos el primer bloque numérico que encuentre
                primer_numero = bloques_numericos[0]

                # REGLA: Si supera los 4 dígitos se descarta, ya que los números de un id ticket no superan los 4 digitos
                if len(primer_numero) > 4:
                    return np.nan

                return f"NAN-{primer_numero}" # si el número es valido lo coloca como NAN-número

            # Si el texto no tiene números (ej. "SIN NÚMERO", "NO LOCE").
            return np.nan

        # Aplicar el formateo a la columna
        df["Número de Ticket"] = df["Número de Ticket"].apply(formatear_ticket)

    # REEMPLAZO DE SIGLAS EN TICKETS NAN-NUMERO
    # El siguiente bloque se ejecuta después de haber formateado 'Número de Ticket' y 'CLIENTE_MAESTRO_ENCONTRADO'.
    # Debido a que en el bloque anterior muchos tickets quedaron grabados con el prefijo temporal "NAN-número",
    # el siguiente bloque busca corregirlos cruzando la información con el maestro de clientes, para colocarle la sigla correcta al ticket
    if "Número de Ticket" in df.columns:
        print(
            "Buscando siglas correspondientes para tickets genéricos (NAN-número)..."
        )

        # Crea un diccionario de mapeo rápido entre el CLIENTE y su SIGLA desde el maestro
        # Elimina duplicados y se asegura que no haya valores nulos en el maestro antes de crear el diccionario
        df_maestro_limpio = df_maestro.dropna(subset=["CLIENTE", "SIGLAS"])
        mapeo_siglas = pd.Series(
            df_maestro_limpio["SIGLAS"].values,
            index=df_maestro_limpio["CLIENTE"],
        ).to_dict()

        # Función interna para procesar fila por fila de la encuesta_soporte
        def reemplazar_nan_por_sigla(fila):
            ticket = str(fila["Número de Ticket"])

            # Identificar si el ticket está catalogado bajo el patrón "NAN-número"
            if ticket.startswith("NAN-"):
                # Se extrae la parte numérica (por ejemplo: de 'NAN-123' tomamos '123')
                numero_ticket = ticket.split("-")[1]
                # Obtenemos el nombre del cliente real que encontramos previamente con fuzzy
                cliente_encontrado = fila.get("CLIENTE_MAESTRO_ENCONTRADO")

                # Si encontramos un cliente válido en el maestro para esta fila
                if (
                    pd.notna(cliente_encontrado)
                    and cliente_encontrado != "SIN COINCIDENCIA SEGURA"
                ):  
                    # Buscamos la sigla en nuestro diccionario de mapeo
                    sigla = mapeo_siglas.get(cliente_encontrado)

                    # Si el cliente tiene una sigla asignada en el maestro, estructuramos el nuevo ticket
                    if pd.notna(sigla) and str(sigla).strip() != "":
                        return f"{str(sigla).strip().upper()}-{numero_ticket}"

            # Si no era un ticket NAN o no se encontró sigla, se deja el valor original
            return fila["Número de Ticket"]

        # Aplicar la función a lo largo del dataframe (fila por fila)
        df["Número de Ticket"] = df.apply(reemplazar_nan_por_sigla, axis=1)

        print("¡Reemplazo de siglas completado con éxito!")
    

    # Diccionario de columnas útiles y sus nuevos nombres cortos
    columnas_utiles = {
        "ID": "ID",
        "Hora de inicio": "Fecha_Inicio",
        "Hora de finalización": "Fecha_Fin",
        "NOMBRE_COMPANIA": "Compania",
        "Número de Ticket": "ID_Ticket",
        "¿Cómo califica la atención y amabilidad del personal que lo atendió?": "Calificacion_Atencion",
        "¿Cómo califica el tiempo de respuesta a la atención del ticket/solicitud reportado?": "Calificacion_Tiempo_Respuesta",
        "¿La solución entregada resolvió el problema reportado?": "Calificacion_Resolucion_Problema",
        "¿Tienes alguna sugerencia que nos ayude a mejorar nuestros servicios?": "Sugerencia",
        "Seleccione el personal que atendió el ticket/solicitud": "Agente"
    }

    # Seleccionar solo las columnas con datos y renombrarlas
    df = df[list(columnas_utiles.keys())].rename(columns=columnas_utiles)

    # Dejar solo el primer nombre del agente:
    df["Agente"] = df["Agente"].astype(str).str.strip().str.split().str[0]

    # --- ENVIAR A SILVER-----
    # Se carga la configuración del yaml
    with open ("config/config.yaml", "r") as file:
            config = yaml.safe_load(file)

    # Se construye la ruta uniendo el directorio silver + nombre archivo limpio
    directorio_silver = config["paths"]["silver_dir"]
    ruta_salida = os.path.join(directorio_silver, "encuesta_soporte_cleaned.xlsx")

    # Guardar el archivo en data/silver
    df.to_excel(ruta_salida, index=False)

    return df