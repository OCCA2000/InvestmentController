import os
import time
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

# Configura las credenciales de la base de datos


# db_config = {
#     'user': 'mecsistel',
#     'password': 'u~J]Y(HTm=FU',
#     'host': '50.31.177.149',
#     'database': 'mecsistel_investment',
#     'raise_on_warnings': True
# }


db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'investment',
    'raise_on_warnings': True
}


# Ruta del archivo Excel
aaaa=time.strftime("%Y")
mm=time.strftime("%m")
dd=time.strftime("%d")
dia=time.strftime("%A")
carpeta='007_CotizacionesHistoricas'
nombre = 'facturas-comerciales'
ext = '.xls'
directorioBase='Z:\\DatosBVQ\\'
nombre = 'facturas-comerciales'
excel_file_path = directorioBase+aaaa+'_'+mm+'\\'+aaaa+'_'+mm+'_'+dd+'\\'+carpeta+'\\'+nombre+'_'+aaaa+'_'+mm+'_'+dd+ext
print ("-->")
print (excel_file_path)
print ("<--")

df = pd.read_excel(excel_file_path, sheet_name=aaaa, skiprows=7, usecols=lambda x: x not in [0])




# Conéctate a la base de datos MySQL
try:
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Elimina la tabla si existe
    cursor.execute("DROP TABLE facturas_his_jao")

    # Crea una conexión a la base de datos usando sqlalchemy
    engine = create_engine('mysql+mysqlconnector://{user}:{password}@{host}/{database}'.format(**db_config))

    # Crea la tabla en la base de datos
    df[:0].to_sql('facturas_his_jao', con=engine, if_exists='replace', index=False)  # Solo crea la estructura de la tabla

    # Carga los datos en la tabla de MySQL
    df.to_sql('facturas_his_jao', con=engine, if_exists='append', index=False)

    # Confirma los cambios
#    cnx.commit()
    print("Datos cargados exitosamente en la tabla 'facturas_his_jao'.")

    
    SQL = "insert into facturas_his (FECHA, EMISOR, PRECIO_PORC, VALOR_NOMINAL, VALOR_EFECTIVO, EMISION, VENCIMIENTO, RENDIMIENTO, PROCEDENCIA, OBSERVACIONES) SELECT `FECHA`, `EMISOR`, `PRECIO %%`, `VALOR NOMINAL (USD)`, `VALOR EFECTIVO (USD)`, `F. EMISION`, `F. VENCIMIENTO`, `RENDIMIENTO %%`, `PROCEDENCIA`, `OBSERVACIONES` FROM `facturas_his_jao` where emisor is not null and fecha >= '" + aaaa + "-" + mm + "-" + dd +"'"

    print(SQL)
    
    cursor.execute(SQL)

 
    print("Actualizada la tabla 'facturas_his'.")

    
    cnx.commit()

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Cierra la conexión
    if 'cnx' in locals() and cnx.is_connected():
        cursor.close()
        cnx.close()
        print("Conexión cerrada.")
