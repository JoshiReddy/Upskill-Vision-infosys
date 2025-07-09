import sys, os, bcrypt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify, make_response
from create_tables import create_tables
from db_connection import get_db_connection
from authentication_helpers import generate_otp, generate_jwt, hash_password, delete_user_sessions, save_session_to_db
import mysql
import requests
from datetime import datetime
from flask_cors import CORS
from kafka_producer import produce_message
app = Flask(__name__)
create_tables()
CORS(app, supports_credentials=True)


@app.route('/api/authentication/', methods=['GET', 'POST'])
def authentication():
    return jsonify({"message": "Authentication service is working!"})
@app.route('/api/authentication/registration-otp-request', methods=['POST'])
def registration_otp_request():
    data = request.json
    email = data.get("email")
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        connection.database = "UpSkill_1"
        otp = generate_otp()
        produce_message('sending_otp', {"email": email, "otp": otp})
        cursor.execute("""
            INSERT INTO otp (email, otp)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
            otp = VALUES(otp)
    """, (email, otp))
        connection.commit()
        return jsonify({"message": "OTP Sent", "status": "success"}), 200
   
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error connecting to database: {err}", "status": "error"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/authentication/verify-registration', methods=["POST"])
def verify_registration():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    designation = data.get("designation")
    otp = data.get("otp")
    password = data.get("password")
    try:
        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM otp WHERE email = %s", (email,))
        user = cursor.fetchone()
        if int(otp) == user[0]:
            encrypted_token = generate_jwt(email)
            hashed_password = hash_password(password)
            cursor.execute("""
                INSERT INTO userdetails (email, phone, name, designation, password)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    phone = VALUES(phone),
                    name = VALUES(name),
                    designation = VALUES(designation)
            """, (email, phone, name, designation, hashed_password))
            connection.commit()
            # Create the response
            response = make_response(jsonify({
                "message": "Registration Successful",
                "status": "success",
                "token": encrypted_token.decode('utf-8')
            }))
            return response, 200

        else:
            return jsonify({"message": "Invalid OTP"}), 401
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error connecting to database: {err}", "status": "error"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/authentication/login-verification', methods=['POST'])
def verify_data():
    print("request received")
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    try:
        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM userdetails WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
            otp = generate_otp()
            produce_message('sending_otp', {"email": email, "otp": otp})
            cursor.execute("""
                INSERT INTO otp (email, otp)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                otp = VALUES(otp)
        """, (email, otp))
            connection.commit()
            return jsonify({"message": "Data matches and OTP sent!", "status": "success"}), 200
        else:
            return jsonify({"message": "Invalid username or password", "status": "error"}), 400

    except mysql.connector.Error as err:
        return jsonify({"message": f"Error connecting to database: {err}", "status": "error"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route("/api/authentication/verify-otp", methods=["POST"])
def generate_otp_route():
    print("verify-otp")
    data = request.json
    req_otp = data.get("otp")
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    try:
        # Save details to the database
          # Use the function from db_connection.py
        connection = get_db_connection()
        cursor = connection.cursor()
        connection.database = "UpSkill_1"
        cursor.execute("SELECT * FROM otp WHERE email = %s", (email,))
        user = cursor.fetchone()
        if int(req_otp) == user[0]:
            delete_user_sessions(email)
            token = generate_jwt(email)
            
            
            response = make_response(jsonify({
                "message": "Data matches!",
                "status": "success",
                "token":token.decode('utf-8')
            }))
            save_session_to_db(email, token)
            return response, 200
        else:
            return jsonify({"message": "Invalid OTP", "status": "error"}), 400
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"error": "Database error"}), 500
    finally:
        connection.commit()
        cursor.close()
        connection.close()

@app.route('/api/authentication/protected', methods=['POST'])
def protected():
    # print("reaa")
    connection = None
    data = request.json
    token = data.get("token")
    if not token:
        # print(token)
        return jsonify({"message": "Unauthorized NO Token"}), 401
    try:
        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM otp WHERE token = %s", (token,))
        user = cursor.fetchone()
        # print(user)
        if user:
            if user[3] < datetime.now():
                return jsonify({'error': 'Session expired'}), 401
            cursor.execute("SELECT * FROM userdetails WHERE email = %s", (user[1],))
            user_details = cursor.fetchone()
            name = user_details[2]
            if user_details[3] == "hradmin" and user_details[5]==1:
                query = """
                SELECT email, status, phone, name, designation
                FROM userdetails 
            """
                cursor.execute(query)
                data = cursor.fetchall()
                return jsonify({"message": "Token is valid","authority":"hradmin", "content":data, "name":name , "email":user[1]}), 200
            elif user_details[3] == "manager" and user_details[5]==1:
                query = """
                    SELECT email, status, phone, name, designation
                    FROM userdetails
                    WHERE designation != 'hradmin' OR (designation = 'hradmin' AND status = 1)
                """
                cursor.execute(query)
                data = cursor.fetchall()
                return jsonify({"message": "Token is valid","authority":"manager", "content":data, "name":name , "email":user[1]}), 200
            elif user_details[3] == "instructor" and user_details[5]==1:
                query = """
                    SELECT email, status, phone, name, designation
                    FROM userdetails
                    WHERE designation = 'participant'
                """
                cursor.execute(query)
                print("instructor")
                data = cursor.fetchall()
                return jsonify({"message": "Token is valid","authority":"instructor", "content":data, "name":name, "email":user[1]}), 200
            elif user_details[3] == "participant" and user_details[5]==1:
                return jsonify({"message": "Token is valid","authority":"participant", "content":"Courses are yet to be added. Please check back later", "name":name}), 200
            else:
                return jsonify({"message": "Token not exists or account under validation","underReview":"account under validation"}), 401
        else:
            return jsonify({"message": "User not found"}), 404
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"error": "Database error"}), 500
    finally:
        connection.commit()
        cursor.close()
        connection.close()
@app.route('/api/authentication/logout', methods=['POST'])
def logout():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
        token = data.get("token")
        if not token:
            return jsonify({'error': 'Session not found'}), 401
        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM otp WHERE token = %s", (token,))
        session = cursor.fetchone()
        if not session:
            return jsonify({'error': 'Session does not exist'}), 404
        cursor.execute("DELETE FROM otp WHERE token = %s", (token,))
        connection.commit()
        cursor.close()
        connection.close()
        response = jsonify({'message': 'Logged out successfully'})
        return response

    except Exception as e:
        print(f"Error during logout: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/authentication/verify-mail', methods=["POST"])
def verifymail():
    data = request.json
    email = data.get("email")
    try:
        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM userdetails WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            otp = generate_otp()
            produce_message('sending_otp', {"email": email, "otp": otp})
            cursor.execute("""
            INSERT INTO otp (email, otp)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
            otp = VALUES(otp)
        """, (email, otp))
            connection.commit()
            return jsonify({"message": "Email found and OTP sent!", "status": "success"}), 200          
        else:
            return jsonify({"message": "Email not exixts", "status": "error"}), 400
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error connecting to database: {err}", "status": "error"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/authentication/update-password', methods=["POST"])
def update_password():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    try:
        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        # Query the database for the username and password
        cursor.execute("SELECT * FROM userdetails WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            cursor.execute(
        "UPDATE userdetails SET password = %s WHERE email = %s",
            (hashed_password, email)
        )
        connection.commit()  # Save changes to the database
        return jsonify({"message": "Password updated!", "status": "success"}), 200
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error connecting to database: {err}", "status": "error"}), 500
    finally:
        cursor.close()
        connection.close()

def update_user(token):
    connection = get_db_connection()
    connection.database = "UpSkill_1"
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM otp WHERE token = %s", (token,))
    user = cursor.fetchone()
    if user:
        # cursor.execute("SELECT * FROM credentials WHERE email = %s", (user[1],))
        # user1 = cursor.fetchone()
        cursor.execute("SELECT * FROM userdetails WHERE email = %s", (user[1],))
        user_details = cursor.fetchone()
        # Proceed with your logic if the token is valid
        if user_details[3] == "hradmin" and user_details[5]==1:
            query = """
            SELECT email, status, phone, name, designation
            FROM userdetails 
        """
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        elif user_details[3] == "manager" and user_details[5]==1:
            query = """
                SELECT email, status, phone, name, designation
                FROM userdetails
                WHERE designation != 'hradmin' OR (designation = 'hradmin' AND status = 1)
            """
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        
@app.route('/api/authentication/approve_user', methods=['POST'])
def approve_user():
    try:
        data = request.get_json()  # Parse JSON request body
        user_id = data.get('userId')
        token = data.get('token')
        # print(token)
        # Update user status in the database
        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()
        query = "UPDATE userdetails SET status = 1 WHERE email = %s"
        cursor.execute(query, (user_id,))
        connection.commit()
        updated_user = update_user(token)
        # print(updated_user)
        return jsonify({'message': f'User {user_id} approved successfully.', "content":updated_user}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/authentication/reject_user', methods=['DELETE'])
def reject_user():
    try:
        data = request.get_json()  # Parse JSON request body
        user_id = data.get('userId')
        token = data.get('token')
        # print(token)
        # Delete user from the database
        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()
        query = "DELETE FROM userdetails WHERE email = %s"
        cursor.execute(query, (user_id,))
        connection.commit()
        updated_user = update_user(token)

        return jsonify({'message': f'User {user_id} rejected successfully.', "content":updated_user}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/fetch_userdetails', methods=['POST'])
def get_user_details():
    try:
        data = request.get_json()  # Parse JSON payload
        token = data.get("token")
        if not token:
            return jsonify({"error": "Token is required"}), 400

        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()

        # Query to fetch email using the token
        query = "SELECT email FROM otp WHERE token = %s"
        cursor.execute(query, (token,))
        email_row = cursor.fetchone()

        if not email_row:  # Check if the token exists in the DB
            return jsonify({"error": "Invalid token"}), 404

        email = email_row[0]

        # Query to fetch user details
        cursor.execute("SELECT * FROM userdetails WHERE email = %s", (email,))
        user_details = cursor.fetchall()
        cursor.execute("SELECT email FROM userdetails")
        all_emails = cursor.fetchall()
        if not user_details:  # Check if user details are found
            return jsonify({"error": "User not found"}), 404
        return jsonify({"user_detail": user_details, "emails":all_emails}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Cleanup database resources
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
