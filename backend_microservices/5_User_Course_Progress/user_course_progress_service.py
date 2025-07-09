from flask import Flask, jsonify, request
from create_tables import create_tables
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_connection import get_db_connection
from flask_cors import CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)
create_tables()
@app.route('/api/user_course_progress/', methods=['GET', 'POST'])
def user_course_progress():
    return jsonify({"message": "User Course Progress service is working!"})

@app.route('/api/user_course_progress/courses/<course_id>', methods=['POST'])
def fetch_course_(course_id):
    data = request.get_json()
    token = data.get("token")
    connection = get_db_connection()
    connection.database = "UpSkill_1"
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM otp WHERE token = %s", (token,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM userdetails WHERE email = %s", (user[1],))
    user_details = cursor.fetchone()
    name = user_details[2]
    connection.database = "UpSkill_5"
    cursor.execute("""
        SELECT m.module_id, m.title, m.learning_points, ump.progress_percentage, ump.completion_status
        FROM modules m
        LEFT JOIN user_module_progress ump
        ON m.module_id = ump.module_id AND ump.email = %s
        WHERE m.courseid = %s
    """, (user[1], course_id))
    modules = cursor.fetchall()

    if not modules:
        return jsonify({"message":"No course available", "id":course_id}), 404

    cursor.execute("""
        SELECT courseid, title, description, instructor, start_date, end_date, duration, introduction
        FROM coursedetails
        WHERE courseid = %s
    """, (course_id,))
    course_details = cursor.fetchone()
    cursor.execute("SELECT progress_percentage FROM user_courses WHERE courseid=%s AND email=%s",(
        course_id, user[1]
    ))
    percentage = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return jsonify({"modules":modules, "courseDetails":course_details, "name":name, "percentage":percentage}), 200

@app.route('/api/user_course_progress/lessons_quizzes/<course_id>', methods=['GET'])
def get_lessons_and_quizzes(course_id):
    auth_header = request.headers.get('Authorization')
    connection = get_db_connection()
    connection.database = "UpSkill_1"
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM otp WHERE token=%s", (auth_header,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"message":"User Not found"}), 404
    connection.database = "UpSkill_5"
    cursor.execute("SELECT * FROM quizzes WHERE module_id = %s", (course_id,))
    quizzes = cursor.fetchall()
    cursor.execute("SELECT * FROM lessons WHERE module_id = %s", (course_id,))
    lessons = cursor.fetchall()
    lesson_ids = [user[0] for user in lessons]
    lesson_ids_placeholders = ', '.join(['%s'] * len(lesson_ids))
    lesson_id_query = f"SELECT completion_status FROM user_lesson_progress WHERE lesson_id IN ({lesson_ids_placeholders}) AND email = %s"
    cursor.execute(lesson_id_query, (*lesson_ids, user[0]))
    lesson_status = cursor.fetchall()

    quiz_ids = [user[0] for user in quizzes]
    quiz_ids_placeholders = ', '.join(['%s'] * len(quiz_ids))
    quiz_id_query = f"SELECT * FROM user_quiz_scores WHERE quiz_id IN ({quiz_ids_placeholders}) AND email = %s"
    cursor.execute(quiz_id_query, (*quiz_ids, user[0]))
    quiz_status = cursor.fetchall()
    print(quiz_ids)
    print(quiz_ids_placeholders)
    print(quiz_status)
    combined_data = {
        "quizzes": [
            {
                "quiz_id": quiz[0],
                "module_id": quiz[1],
                "title": quiz[2],
                "status": quiz_status[index][4] if index < len(quiz_status) else None
            }
            for index, quiz in enumerate(quizzes)
        ],
        "lessons": [
            {
                "lesson_id": lesson[0],
                "module_id": lesson[1],
                "title": lesson[2],
                "description": lesson[3],
                "status": lesson_status[index][0] if index < len(lesson_status) else None
            }
            for index, lesson in enumerate(lessons)
        ]
    }

    return jsonify({"moduleData":combined_data, "quizScores":quiz_status})

@app.route('/api/user_course_progress/mark_lesson_as_read/<lesson_id>', methods=['POST'])
def set_mark_as_read(lesson_id):
    auth_header = request.headers.get('Authorization')
    data = request.get_json()
    module_id = data.get("moduleId")
    percentage = data.get("percentage")
    connection = get_db_connection()
    connection.database = "UpSkill_1"
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM otp WHERE token=%s", (auth_header,))
    user = cursor.fetchone()
    
    if not user:
        return jsonify({"message":"User Not found"}), 404
    connection.database = "UpSkill_5"

    cursor.execute(
        """
        INSERT INTO user_lesson_progress (lesson_id, email, completion_status)
        VALUES (%s, %s, 'completed')
        ON DUPLICATE KEY UPDATE completion_status='completed'
        """,
        (lesson_id, user[0])
    )
    connection.commit()

    cursor.execute(
        """
        INSERT INTO user_module_progress (module_id, email, progress_percentage, completion_status)
        VALUES (%s, %s, %s, 'in progress')
        ON DUPLICATE KEY UPDATE progress_percentage = %s, completion_status = 'in progress'
        """,
        (module_id, user[0], percentage, percentage)
    )

    connection.commit()

    if percentage == 100:
        cursor.execute(
            """
            INSERT INTO user_module_progress (module_id, email, progress_percentage, completion_status)
            VALUES (%s, %s,100, 'completed')
            ON DUPLICATE KEY UPDATE completion_status='completed'
            """,
            (module_id, user[0])
        )
        connection.commit()

    return jsonify({"message":"success"}), 200

@app.route('/api/user_course_progress/update_module_status', methods=['POST'])
def update_module():
    data = request.get_json()
    module_id = data.get("moduleId")
    percentage = data.get("percentage")
    token = request.headers.get('Authorization')
    connection = get_db_connection()
    connection.database = "UpSkill_1"
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM otp WHERE token=%s", (token,))
    user = cursor.fetchone()
    print(percentage)
    connection.database = "UpSkill_5"
    if percentage >= 100:
        cursor.execute(
            """
            INSERT INTO user_module_progress (module_id, email, completion_status, progress_percentage)
            VALUES (%s, %s, 'completed', 100)
            ON DUPLICATE KEY UPDATE completion_status='completed', progress_percentage=100
            """,
            (module_id, user[0])
        )

        connection.commit()
        return jsonify({"complete":"success"}), 200
    else:
        return jsonify({"incomplete":"Complete full module"}), 200
    
@app.route('/api/user_course_progress/fetch_quizzes/<quiz_id>', methods=['GET'])
def fetch_quizzes(quiz_id):
    connection = get_db_connection()
    connection.database = "UpSkill_5"
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT 
        qz.quiz_id, qz.title, 
        qs.question_id, qs.question_text,
        opt.option_id, opt.option_text, opt.is_correct
    FROM quizzes qz
    JOIN quiz_questions qs ON qz.quiz_id = qs.quiz_id
    JOIN quiz_options opt ON qs.question_id = opt.question_id
    WHERE qz.quiz_id = %s
    """
    cursor.execute(query, (quiz_id,))
    results = cursor.fetchall()
    quiz_data = {
        "quiz_id": quiz_id,
        "title": results[0]["title"],
        "questions": {}
    }

    for row in results:
        question_id = row["question_id"]
        if question_id not in quiz_data["questions"]:
            quiz_data["questions"][question_id] = {
                "question_text": row["question_text"],
                "options": []
            }
        quiz_data["questions"][question_id]["options"].append({
            "option_id": row["option_id"],
            "option_text": row["option_text"],
            "is_correct": row["is_correct"]
        })

    return jsonify({"message":"success", "quizData":quiz_data}), 200

@app.route('/api/user_course_progress/submitting_quizzes/<quiz_id>', methods=['POST'])
def submit_quizzes(quiz_id):
    data = request.get_json()
    token = data.get("token")
    score = data.get("score")
    total_score = data.get("totalScore")
    connection = get_db_connection()
    connection.database = "UpSkill_1"
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM otp WHERE token=%s", (token,))
    user = cursor.fetchone()

    pass_fail_status = "pass" if (score / total_score) * 100 >= 50 else "fail"
    connection.database = "UpSkill_5"
    cursor.execute(
        """
        INSERT INTO user_quiz_scores (quiz_id, email, pass_fail_status, total_score, score, attempt_date)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE pass_fail_status=%s, total_score=%s, score=%s, attempt_date=NOW()
        """,
        (quiz_id, user[0], pass_fail_status, total_score, score, pass_fail_status, total_score, score)
    )
    connection.commit()

    return jsonify({"message":"success"}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
