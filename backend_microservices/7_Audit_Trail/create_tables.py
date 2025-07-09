import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_connection import get_db_connection
from mysql.connector import Error


create_audit_trail_table = """
CREATE TABLE IF NOT EXISTS audit_trail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    courseid VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(150) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action VARCHAR(45) DEFAULT NULL
);
"""
table_creation_queries = [
    create_audit_trail_table,

]

def create_tables():
    connection = None
    try:
        connection = get_db_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS UpSkill_7;")
            print("Database UpSkill_7 created or already exists.")
            connection.database = "UpSkill_7"
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
        
