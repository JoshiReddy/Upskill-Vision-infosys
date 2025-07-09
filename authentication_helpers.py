import random, os, bcrypt, jwt, uuid, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from db_connection import get_db_connection
import mysql
JWT_SECRET = os.getenv("JWT_SECRET_TOKEN")
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def generate_jwt(email):
    payload = {
        'email': email+str(uuid.uuid4()),
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    encrypted_token = cipher.encrypt(token.encode('utf-8'))
    return encrypted_token

def generate_otp():
    return random.randint(100000, 999999)

def save_session_to_db(email, token):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        connection.database = "UpSkill_1"
        expiry = datetime.now() + timedelta(hours=1)
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        cursor.execute("""
            INSERT INTO otp (email, token, expiry)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            token = VALUES(token),
            expiry = VALUES(expiry)
        """, (email, token, expiry))

        # print("33")
        connection.commit()
        print("token saved")
        return True
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False

def delete_user_sessions(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        connection.database = "UpSkill_1"
        cursor.execute("DELETE FROM otp WHERE email = %s", (user_id,))
        print("token deleted")
        connection.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False
