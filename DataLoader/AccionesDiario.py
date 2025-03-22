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
nombre = 'acciones'
ext = '.xls'
directorioBase='Z:\\DatosBVQ\\'
nombre = 'acciones'
excel_file_path = directorioBase+aaaa+'_'+mm+'\\'+aaaa+'_'+mm+'_'+dd+'\\'+carpeta+'\\'+nombre+'_'+aaaa+'_'+mm+'_'+dd+ext
print ("-->")
print (excel_file_path)
print ("<--")


# Carga los datos desde la pestaña "2023" del archivo Excel, omitiendo la primera columna (skipcols=[0])
df = pd.read_excel(excel_file_path, sheet_name=aaaa, skiprows=8, usecols=lambda x: x not in [0])


# Conéctate a la base de datos MySQL
try:
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Elimina la tabla si existe
    cursor.execute("DROP TABLE shares_jao")

    # Crea una conexión a la base de datos usando sqlalchemy
    engine = create_engine('mysql+mysqlconnector://{user}:{password}@{host}/{database}'.format(**db_config))

    # Crea la tabla en la base de datos
    df[:0].to_sql('shares_jao', con=engine, if_exists='replace', index=False)  # Solo crea la estructura de la tabla

    # Carga los datos en la tabla de MySQL
    df.to_sql('shares_jao', con=engine, if_exists='append', index=False)

    # Confirma los cambios
#    cnx.commit()
    print("Datos cargados exitosamente en la tabla 'shares_jao'.")

    SQL = "insert into shares (`SHA_ISSUER_ID`, `SHA_DATE`, `SHA_ISSUER`, `SHA_TYPE`, `SHA_NOMINAL_VALUE`, `SHA_PRICE`, `SHA_NUMBER`, `SHA_CASH_VALUE`, `SHA_PROVENANCE`) select '1', FECHA, EMISOR, VALOR, `VALOR NOMINAL` , PRECIO, `NUMERO ACCIONES`, `VALOR EFECTIVO`,PROCEDENCIA FROM shares_jao where `NUMERO ACCIONES` <> 0 AND fecha >= '" + aaaa + "-" +mm + "-" + dd +"'"
#    SQL = "insert into shares (`SHA_ISSUER_ID`, `SHA_DATE`, `SHA_ISSUER`, `SHA_TYPE`, `SHA_NOMINAL_VALUE`, `SHA_PRICE`, `SHA_NUMBER`, `SHA_CASH_VALUE`, `SHA_PROVENANCE`) select '1', FECHA, EMISOR, VALOR, `VALOR NOMINAL` , PRECIO, `NUMERO ACCIONES`, `VALOR EFECTIVO`,PROCEDENCIA FROM shares_jao where `NUMERO ACCIONES` <> 0 AND fecha > '" + aaaa + "-" +mm + "dd'"
    print(SQL)
    
    cursor.execute(SQL)

 
    
    SQL = "UPDATE shares A JOIN dictionary D ON A.SHA_ISSUER = D.DIC_VALUE SET A.SHA_ISSUER_ID = D.DIC_ID"

    cursor.execute(SQL)

    print("Actualizada la tabla 'shares'.")


    #SQL = "call SP_SHARES_LAST_DATE" ;

    cursor.execute(SQL)
    
    cnx.commit()

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Cierra la conexión
    if 'cnx' in locals() and cnx.is_connected():
        cursor.close()
        cnx.close()
        print("Conexión cerrada.")
