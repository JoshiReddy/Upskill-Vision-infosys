from flask import Flask, request, jsonify, make_response

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_connection import get_db_connection
import requests
app = Flask(__name__)
from flask_cors import CORS
CORS(app, supports_credentials=True)


@app.route('/api/student_course/', methods=['GET', 'POST'])
def student_course():
    return jsonify({"message": "Student Course service is working!"})

@app.route('/api/student_course/courses', methods=["POST"])
def courses():
    try:
        # Extract data and token from the request
        data = request.get_json()
        token = data.get('token')

        # Validate token
        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM otp WHERE token = %s", (token,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Invalid token"}), 401

        # Get filter status from query parameters
        filter_status = request.args.get('filter', 'all')  # Default filter: 'all'

        # Define SQL query based on filter status
        if filter_status == 'enrolled':
            query = """
                SELECT c.courseid, c.title, c.description, c.instructor, c.start_date, c.end_date, c.duration, 'Enrolled' AS status
                FROM coursedetails c
                JOIN user_courses uc ON c.courseid = uc.courseid
                WHERE uc.email = %s AND uc.status = 'enrolled';
            """
        elif filter_status == 'completed':
            query = """
                SELECT c.courseid, c.title, c.description, c.instructor, c.start_date, c.end_date, c.duration, 'Completed' AS status
                FROM coursedetails c
                JOIN user_courses uc ON c.courseid = uc.courseid
                WHERE uc.email = %s AND uc.status = 'completed';
            """
        else:  # Default: 'all'
            query = """
                SELECT c.courseid, c.title, c.description, c.instructor, c.start_date, c.end_date, c.duration,
                       IFNULL(uc.status, 'Not Enrolled') AS status
                FROM coursedetails c
                LEFT JOIN user_courses uc ON c.courseid = uc.courseid AND uc.email = %s;
            """

        # Execute query
        connection.database = "UpSkill_5"
        cursor.execute(query, (user[1],))
        courses = cursor.fetchall()

        # Format response
        result = [
            {
                "courseid": course[0],
                "title": course[1],
                "description": course[2],
                "instructor": course[3],
                "start_date": course[4],
                "end_date": course[5],
                "duration": course[6],
                "status": course[7]
            }
            for course in courses
        ]

        return jsonify(result), 200

    except Exception as e:
        # Log the error for debugging purposes
        print("Error fetching courses:", str(e))
        return jsonify({"error": "An error occurred while fetching courses"}), 500

    finally:
        # Ensure cursor and connection are properly closed
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        except Exception as cleanup_error:
            print("Error during cleanup:", str(cleanup_error))

@app.route('/api/student_course/enroll', methods=["POST"])
def enroll_course():
    try:
        data = request.get_json()
        token = data.get('token')
        course_id = data.get('courseid')

        if not token or not course_id:
            return jsonify({"error": "Missing token or course ID"}), 400

        connection = get_db_connection()
        connection.database = "UpSkill_1"
        cursor = connection.cursor()

        # Get user details using token
        cursor.execute("SELECT email FROM otp WHERE token = %s", (token,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Invalid token"}), 401

        email = user[0]
        connection.database = "UpSkill_5"
        cursor.execute(
            "INSERT INTO user_courses (email, courseid, status) VALUES (%s, %s, %s)",
            (email, course_id, 'enrolled')
        )
        connection.commit()

        return jsonify({"message": "Successfully enrolled in the course"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Ensure cursor and connection are properly closed
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        except Exception as cleanup_error:
            print("Error during cleanup:", str(cleanup_error))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
