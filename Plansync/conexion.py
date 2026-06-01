import os
import mysql.connector

def conectar():

    conexion = mysql.connector.connect(

        host=os.getenv("MYSQLHOST"),
        port=int(os.getenv("MYSQLPORT", 49847)),
        user="root",
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")

    )

    return conexion