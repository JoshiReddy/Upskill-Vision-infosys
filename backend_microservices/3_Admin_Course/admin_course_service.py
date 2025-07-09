import os, sys
from flask import Flask, jsonify, request

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_connection import get_db_connection
from flask_cors import CORS
import requests
from kafka_producer import produce_message

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/api/admin_course/', methods=['GET', 'POST'])
def admin_course():
    return jsonify({"message": "Admin Course service is working!"})

@app.route('/api/admin_course/fetch-courses', methods=["GET"])
def fetch_courses():
    try:
        connection = get_db_connection()
        connection.database = "UpSkill_5"
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM coursedetails")
        courses = cursor.fetchall()
        return jsonify({"message": "Course fetch successful", "content": courses})
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"message": "Failed to fetch courses", "error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Update Course
@app.route('/api/admin_course/update-course/<course_id>', methods=["PUT"])
def update_course(course_id):
    connection = get_db_connection()
    connection.database = "UpSkill_5"
    cursor = connection.cursor()
    data = request.get_json()
    name = data.get("name")
    instructor = data.get("instructor")
    description = data.get("description")
    start_date = data.get("startDate")
    end_date = data.get("endDate")
    duration = data.get("duration")
    token = data.get("token")
    if not name or not instructor or not description or not start_date or not end_date:
        connection.close()
        return jsonify({"message": "Missing required fields", "status": "error"}), 400
    cursor.execute("SELECT * FROM coursedetails WHERE courseid = %s", (course_id,))
    course = cursor.fetchone()
    
    if course is None:
        connection.close()
        return jsonify({"message": "Course not found", "status": "error"}), 404
    
    # Update the course
    cursor.execute("""
        UPDATE coursedetails
        SET title = %s, description = %s, instructor = %s, start_date = %s, end_date = %s, duration=%s
        WHERE courseid = %s
    """, (name, description, instructor, start_date, end_date, duration, course_id))
    connection.commit()
    details_request = requests.post("http://localhost:5001/fetch_userdetails", json={"token":token})
    if details_request.status_code == 200:
        response_data = details_request.json()
        user_details = response_data.get("user_detail")
        all_emails = response_data.get("emails")
        email_list = [email[0] for email in all_emails]
        produce_message('send_notification', {"email_list":email_list, "name":name, "start_date":start_date, "duration":duration})
        produce_message('audit_trail',{"course_id":course_id, "email":user_details[0][0], "name":user_details[0][2], "action":"Course Update"})
        # (message['course_id'], message['email'], message['name'], message['action'])
        # connection.database = "UpSkill_7"
        # cursor.execute(
        #     """INSERT INTO audit_trail (courseid, email, name, timestamp, action)
        #     VALUES (%s, %s, %s, NOW(), "Course Update");""", 
        #     (course_id, user_details[0][0], user_details[0][2])
        # )
        connection.commit()
        connection.close()
        return jsonify({"message": "Course updated successfully", "status": "success"})

    else:
        return jsonify({
            "message": "Failed to fetch user data.",
            "error": details_request.json()
        }), details_request.status_code
    # cursor.execute("SELECT * FROM otp WHERE token = %s", (token,))
    # user = cursor.fetchone()
    # cursor.execute("SELECT * FROM userdetails WHERE email = %s", (user[1],))
    # user_details = cursor.fetchone()

    # cursor.execute(
    #     """INSERT INTO audit_trail (courseid, email, name, timestamp, action)
    #        VALUES (%s, %s, %s, NOW(), "Course Update");
    #     """, 
    #     (course_id, user_details[0], user_details[2])
    # )
    # cursor.execute("SELECT * FROM userdetails")
    # emails = cursor.fetchall()
    # 
    # print(email_list)
    # send_course_update_notification_email(email_list, name, start_date, duration)

@app.route('/api/admin_course/create-course', methods=['POST'])
def create_course():
    data = request.get_json()
    # print(data)
    # Extract course data
    courseId = data.get('courseId')
    courseTitle = data.get('courseTitle')
    description = data.get('description')
    duration = data.get('duration')
    startDate = data.get('startDate')
    endDate = data.get('endDate')
    instructor = data.get('instructor')
    connection = get_db_connection()
    connection.database = "UpSkill_5"
    cursor = connection.cursor()
    token = data.get('token')
    # print(token)

    # Insert course into the database
    cursor.execute("""
        INSERT INTO coursedetails (courseid, title, description, instructor, start_date, end_date, duration )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, ( data['courseId'], 
    data['courseTitle'], 
    data['description'], 
    data['instructor'],
    data['startDate'], 
    data['endDate'],
    data['duration']
     ))
    connection.commit()
    details_request = requests.post("http://localhost:5001/fetch_userdetails", json={"token":token})
    if details_request.status_code == 200:
        response_data = details_request.json()
        user_details = response_data.get("user_detail")
        all_emails = response_data.get("emails")
        email_list = [email[0] for email in all_emails]
        produce_message('send_course_notification', {"email_list":email_list, "name":courseTitle, "start_date":startDate, "duration":duration})
        produce_message('audit_trail',{"course_id":courseId, "email":user_details[0][0], "name":user_details[0][2], "action":"Course Creation"})
    # cursor.execute("SELECT * FROM otp WHERE token = %s", (token,))
    # user = cursor.fetchone()
    # # print(user)
    # cursor.execute("SELECT * FROM userdetails WHERE email = %s", (user[1],))
    # user_details = cursor.fetchone()
    # # print(user_details[0], user_details[2])
    # cursor.execute(
    #     """INSERT INTO audit_trail (courseid, email, name, timestamp, action)
    #        VALUES (%s, %s, %s, NOW(), "Course Create");
    #     """, 
    #     (data['courseId'], user_details[0], user_details[2])
    # )
    # connection.commit()
        cursor.execute("SELECT * FROM coursedetails")
        courses = cursor.fetchall()
    # cursor.execute("SELECT email FROM otp")
    # emails = cursor.fetchall()
    # email_list = [email[0] for email in emails]
    # send_course_notification_email(email_list, data['courseTitle'], data['startDate'], duration)

        return jsonify({'message': 'Course created and emails sent successfully', "updated_courses":courses}), 200
    else:
        return jsonify({
            "message": "Failed to create new course.",
            "error": details_request.json()
        }), details_request.status_code

@app.route('/api/admin_course/delete-course/<course_id>', methods=["DELETE"])
def delete_course(course_id):
    data = request.get_json()
    token = data.get('token')
    connection = get_db_connection()
    connection.database = "UpSkill_5"
    cursor = connection.cursor()
    
    # Check if the course exists
    cursor.execute("SELECT * FROM coursedetails WHERE courseid = %s", (course_id,))
    course = cursor.fetchone()
    
    if course is None:
        connection.close()
        return jsonify({"message": "Course not found", "status": "error"}), 404
    
    # Delete the course
    cursor.execute("DELETE FROM coursedetails WHERE courseid = %s", (course_id,))
    details_request = requests.post("http://localhost:5001/fetch_userdetails", json={"token":token})
    if details_request.status_code == 200:
        response_data = details_request.json()
        user_details = response_data.get("user_detail")
        produce_message('audit_trail',{"course_id":course_id, "email":user_details[0][0], "name":user_details[0][2], "action":"Course Deletion"})
    # cursor.execute("SELECT * FROM otp WHERE token = %s", (token,))
    # user = cursor.fetchone()
    # cursor.execute("SELECT * FROM userdetails WHERE email = %s", (user[1],))
    # user_details = cursor.fetchone()
    # # print(user_details[0], user_details[2])
    # cursor.execute(
    #     """INSERT INTO audit_trail (courseid, email, name, timestamp, action)
    #        VALUES (%s, %s, %s, NOW(), "Course Delete");
    #     """, 
    #     (course_id, user_details[0], user_details[2])
    # )
        connection.commit()
        connection.close()
        
        return jsonify({"message": "Course deleted successfully", "status": "success"})
    else:
        return jsonify({
            "message": "Failed to delete the course.",
            "error": details_request.json()
        }), details_request.status_code

@app.route('/api/courses', methods=["GET"])
def fetch_cours():
    connection = get_db_connection()
    connection.database = "UpSkill_3"
    cursor = connection.cursor()

    # Fetch all course details
    cursor.execute("SELECT * FROM coursedetails")
    courses = cursor.fetchall()

    # Define column names for mapping
    columns = [
        "courseid", "title", "description", "instructor",
        "start_date", "end_date", "created_at", "duration", "notes"
    ]

    # Convert the result into a list of dictionaries
    courses_dicts = [
        dict(zip(columns, course)) for course in courses
    ]

    return jsonify(courses_dicts)

@app.route('/api/admin_course/enrolled-students/<course_id>', methods=['GET'])
def fetch_enrolled_students(course_id):
    try:
        # Step 1: Fetch emails of enrolled students from the first database
        connection = get_db_connection()
        connection.database = "UpSkill_5"  # Database for user_courses and related tables
        cursor = connection.cursor()

        email_query = """
            SELECT email 
            FROM user_courses 
            WHERE courseid = %s
        """
        cursor.execute(email_query, (course_id,))
        email_results = cursor.fetchall()

        if not email_results:
            return jsonify({
                "status": "failure",
                "message": f"No students enrolled for course ID {course_id}"
            }), 200

        # Extract emails into a list
        emails = [row[0] for row in email_results]
        print(emails)
        # Close the first database connection
        cursor.close()
        connection.close()

        # Step 2: Fetch user details from the second database
        connection = get_db_connection()
        connection.database = "UpSkill_1"  # Database for userdetails table
        cursor = connection.cursor()

        user_query = """
            SELECT email, name
            FROM userdetails
            WHERE email IN (%s)
        """ % ','.join(['%s'] * len(emails))
        cursor.execute(user_query, emails)
        user_results = cursor.fetchall()
        print(user_results)
        if not user_results:
            return jsonify({
                "status": "failure",
                "message": "No user details found for the provided emails"
            }), 404

        user_map = {email: name for email, name in user_results}

        # Close the second database connection
        cursor.close()
        connection.close()

        # Step 3: Fetch additional details from the first database again
        connection = get_db_connection()
        connection.database = "UpSkill_5"
        cursor = connection.cursor()

        details_query = """
            SELECT 
                uc.email AS user_email,
                m.title AS module_title,
                ump.completion_status AS module_completion_status,
                ump.progress_percentage AS module_progress,
                q.title AS quiz_title,
                uqs.pass_fail_status AS quiz_completion_status,
                uqs.score AS quiz_score,
                uqs.total_score AS quiz_total_score
            FROM user_courses AS uc
            JOIN modules AS m ON uc.courseid = m.courseid
            LEFT JOIN user_module_progress AS ump ON uc.email = ump.email AND m.module_id = ump.module_id
            LEFT JOIN quizzes AS q ON m.module_id = q.module_id
            LEFT JOIN user_quiz_scores AS uqs ON uc.email = uqs.email AND q.quiz_id = uqs.quiz_id
            WHERE uc.courseid = %s
            ORDER BY uc.email, m.title;
        """
        cursor.execute(details_query, (course_id,))
        details_results = cursor.fetchall()

        if not details_results:
            return jsonify({
                "status": "failure",
                "message": "No additional details found for the enrolled students"
            }), 404

        # Combine user details and additional information
        final_results = []
        for row in details_results:
            email = row[0]
            user_name = user_map.get(email, "Unknown")
            final_results.append((user_name,) + row)

        return jsonify({
            "status": "success",
            "content": final_results
        })

    except Exception as e:
        return jsonify({
            "status": "failure",
            "message": f"Unexpected error: {str(e)}"
        }), 500

    finally:
        # Ensure connections are closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
