import pymysql
from datetime import datetime

base_datos='investment'
tabla='amortization'
hoy=datetime.today()

conn = pymysql.connect(host="localhost",user="root",passwd="",db=base_datos)

cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS amortization_sim")
cursor.execute("CREATE TABLE amortization_sim AS SELECT * FROM amortization")

inv_id = input("Ingrese el identificador de la inversión que desea vender: ")

sql="UPDATE amortization_sim SET am_sold_date = %s, am_expired = 0, is_active = 0, is_deleted = 1 WHERE inv_id = %s AND am_expiration_date >= %s"
valores=(hoy, inv_id, hoy)

cursor.execute(sql, valores)
conn.commit()

print(f"Inversión {inv_id} vendida exitosamente.")

conn.close()

