import mysql.connector

def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Sw@07092005",
        database="plansync"
    )

    return conexion


# Probar conexión
if __name__ == "__main__":
    try:
        conn = conectar()
        print("Conexión exitosa a MySQL")
        conn.close()

    except Exception as e:
        print("Error:", e)