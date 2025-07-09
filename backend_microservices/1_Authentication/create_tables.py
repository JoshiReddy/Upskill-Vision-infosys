import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_connection import get_db_connection
from mysql.connector import Error

create_userdetails_table = """
CREATE TABLE IF NOT EXISTS userdetails (
    email VARCHAR(150) UNIQUE PRIMARY KEY NOT NULL,
    phone VARCHAR(15) NOT NULL,
    name VARCHAR(150) NOT NULL,
    designation VARCHAR(45) NOT NULL,
    password VARCHAR(255) NOT NULL,
    status INT DEFAULT 0
);
"""
create_otp_table = """
CREATE TABLE IF NOT EXISTS otp (
    otp INT DEFAULT NULL,
    email VARCHAR(150) UNIQUE PRIMARY KEY NOT NULL,
    token VARCHAR(1000) DEFAULT NULL,
    expiry DATETIME DEFAULT NULL
);
"""


table_creation_queries = [
    create_userdetails_table,
    create_otp_table,

]

def create_tables():
    connection = None
    try:
        connection = get_db_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS UpSkill_1;")
            print("Database UpSkill_1 created or already exists.")
            connection.database = "UpSkill_1"
            for query in table_creation_queries:
                cursor.execute(query)
        connection.commit()
        print("All tables created successfully.")
    except Error as err:
        print(f"Error occurred: {err}")
        raise
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
        
