import pymysql

base_datos='investment'
tabla='amortization'

conn = pymysql.connect(host="localhost",user="root",passwd="",db=base_datos)

cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS amortization_sim")

cursor.execute("CREATE TABLE amortization_sim AS SELECT * FROM amortization")

inv_id = input("Ingrese el identificador de la inversión que desea vender: ")

print(inv_id)

conn.close()

