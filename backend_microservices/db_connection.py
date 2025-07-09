import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Connection Successfull")
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise     
