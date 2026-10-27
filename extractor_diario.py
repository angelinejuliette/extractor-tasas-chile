import os
import requests
import pandas as pd

SERIES_A_EXTRAER = {
    "Dolar_Observado": "F073.TCO.PRE.Z.D",
    "Euro": "F072.CLP.EUR.N.O.D",
    "Yen_Japones": "F072.JPY.USD.N.O.D",
    "UF": "F073.UFF.PRE.Z.D",
    "UTM": "F073.UTR.PRE.Z.M", 
    "Libra_Cobre_Centavos_USD": "F019.PPB.PRE.100.D",
    "Tasa_Politica_Monetaria_Porcentaje": "F022.TPM.TIN.D001.NO.Z.D"
}

TOKEN = "$2a$10$/jKRDD/7A1qMadE5WpRwcunVvyP/DSuL/TifA5e0RSf6Df.dkmGyy"
URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

datos_consolidados = []

for nombre_tasa, codigo_serie in SERIES_A_EXTRAER.items():
    # Petición sin firstdate ni lastdate para forzar el historial completo
    parametros = {
        "token": TOKEN,
        "function": "GetSeries",
        "timeseries": codigo_serie
    }
    
    respuesta = requests.get(URL, params=parametros)
    datos = respuesta.json()
    
    if datos.get("CodigoError", 0) == 0:
        observaciones = datos.get("Series", {}).get("Obs", [])
        
        if observaciones:
            # Extraer siempre el último valor del historial
            ultimo_dato = observaciones[-1]
            datos_consolidados.append({
                "indicador": nombre_tasa,
                "fecha_valor": ultimo_dato["indexDateString"],
                "valor": float(ultimo_dato["value"])
            })
        else:
            print(f"Sin datos para {nombre_tasa}. Verifica que el código de serie sea el correcto en la BDE.")
    else:
        print(f"Error en {nombre_tasa}: {datos.get('DescripcionError')}")

if datos_consolidados:
    df = pd.DataFrame(datos_consolidados)
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(directorio_script, "tasas_completas.json")
    
    df.to_json(ruta_archivo, orient="records", indent=4)
    print(f"Extracción finalizada. Archivo consolidado guardado en:\n{ruta_archivo}")