from flask import Flask, jsonify, request
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_connection import get_db_connection
from flask_cors import CORS
import mysql
from collections import defaultdict
app = Flask(__name__)
CORS(app, supports_credentials=True)
@app.route('/api/all_users_list/', methods=['GET', 'POST'])
def all_users_list():
    return jsonify({"message": "All Users List service is working!"})


@app.route('/api/all_users_list/user-progress', methods=['POST'])
def get_user_progress():
        data = request.json
        email = data.get("userId")
        token = data.get("token")
        connection = get_db_connection()
        connection.database = "UpSkill_5"
        cursor = connection.cursor(dictionary=True)
       
        # Fetch the total number of courses the user is enrolled in
        total_courses_query = """
        SELECT COUNT(DISTINCT uc.courseid) AS total_courses
        FROM user_courses uc
        WHERE uc.email = %s AND uc.status = 'enrolled';
        """
        cursor.execute(total_courses_query, (email,))
        result = cursor.fetchone()
        total_courses = result['total_courses'] if result else 0

        # Fetch course details, including progress
        courses_query = """
        SELECT
            uc.courseid,
            cd.title AS course_name,
            COUNT(DISTINCT m.module_id) AS total_modules,
            COUNT(DISTINCT CASE WHEN ump.progress_percentage > 0 THEN m.module_id END) AS active_modules,
            COUNT(DISTINCT CASE WHEN ump.progress_percentage = 100 THEN m.module_id END) AS completed_modules,
            SUM(CASE WHEN ulp.completion_status = 'completed' THEN 1 ELSE 0 END) AS lessons_completed,
            SUM(CASE WHEN uqs.score > 0 THEN 1 ELSE 0 END) AS quizzes_completed,
            AVG(ump.progress_percentage) AS overall_progress
        FROM user_courses uc
        LEFT JOIN coursedetails cd ON uc.courseid = cd.courseid
        LEFT JOIN modules m ON uc.courseid = m.courseid
        LEFT JOIN user_module_progress ump ON uc.email = ump.email AND m.module_id = ump.module_id
        LEFT JOIN lessons l ON m.module_id = l.module_id
        LEFT JOIN user_lesson_progress ulp ON uc.email = ulp.email AND l.lesson_id = ulp.lesson_id
        LEFT JOIN quizzes q ON m.module_id = q.module_id
        LEFT JOIN user_quiz_scores uqs ON uc.email = uqs.email AND q.quiz_id = uqs.quiz_id
        WHERE uc.email = %s AND uc.status = 'enrolled'
        GROUP BY uc.courseid
        """
        cursor.execute(courses_query, (email,))
        courses_data = cursor.fetchall()
        # Close the database connection
        cursor.close()
        connection.close()
        print(courses_data)
        return jsonify(courses_data), 200
@app.route('/api/all_users_list/all-users-progress', methods=['GET'])
def get_all_user_progress():
    try:
            # Connect to user_courses database
            connection = get_db_connection()
            connection.database = "UpSkill_5"
            cursor = connection.cursor(dictionary=True)

            # Fetch email, courseid, user name, course name, total modules, and completed modules for each user in one query
            cursor.execute("""
                SELECT 
                    u.email, 
                    u.courseid, 
                    ud.name AS user_name, 
                    cd.title AS course_name, 
                    (SELECT COUNT(*) FROM modules m WHERE m.courseid = u.courseid) AS total_modules,
                    (SELECT COUNT(*) 
                    FROM user_module_progress ump 
                    JOIN modules m ON ump.module_id = m.module_id
                    WHERE ump.email = u.email AND m.courseid = u.courseid AND ump.completion_status = 'completed') AS completed_modules
                FROM 
                    user_courses u
                LEFT JOIN 
                    upskill_1.userdetails ud ON u.email = ud.email
                LEFT JOIN 
                    coursedetails cd ON u.courseid = cd.courseid
            """)


            # Fetch all the data
            user_data = cursor.fetchall()

            # Use defaultdict to accumulate data for each email
            accumulated_data = defaultdict(lambda: {"totalCourses": 0, "total_completed_modules": 0, "total_modules": 0})

            for data in user_data:
                email = data['email']
                total_modules = data['total_modules']
                completed_modules = data['completed_modules']
                
                # Accumulate total courses
                accumulated_data[email]["totalCourses"] += 1
                accumulated_data[email]["total_modules"] += total_modules
                accumulated_data[email]["total_completed_modules"] += completed_modules

            # Prepare the final response data
            users_data = []

            for email, user_info in accumulated_data.items():
                total_modules = user_info["total_modules"]
                completed_modules = user_info["total_completed_modules"]
                print(total_modules, completed_modules)
                user_name = next((data["user_name"] for data in user_data if data["email"] == email), "Unknown")
                # Calculate the overall performance as an average
                overall_performance = (completed_modules / total_modules) * 100 if total_modules else 0
                
                users_data.append({
                    "userName": user_name,  # Assuming the user's name is the same for each email
                    "email": email,
                    "totalCourses": user_info["totalCourses"],
                    "overallPerformance": overall_performance
                })

            # Close the cursor and connection
            cursor.close()
            connection.close()
            print(users_data)
            # return jsonify([{"userName": "John Doe","email": "cscience.tech1@gmail.com","totalCourses": 3,"overallPerformance": 87.5},{"userName": "Jane Smith","email": "elamaran6017@gmail.com","totalCourses": 2,"overallPerformance": 70,}]), 200
            return jsonify(users_data), 200

    except Exception as e:
            print(str(e))
            return jsonify({
                "status": "failure",
                "message": f"Unexpected error: {str(e)}"
            }), 500
        


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
