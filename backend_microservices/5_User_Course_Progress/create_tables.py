import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_connection import get_db_connection
from mysql.connector import Error

create_coursedetails_table = """
CREATE TABLE IF NOT EXISTS coursedetails (
    courseid VARCHAR(150) UNIQUE PRIMARY KEY NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructor VARCHAR(150) NOT NULL,
    start_date VARCHAR(45) NOT NULL,
    end_date VARCHAR(45) NOT NULL,
    changes MEDIUMTEXT DEFAULT NULL,
    duration VARCHAR(45) NOT NULL COMMENT 'Duration in days',
    introduction LONGTEXT 
);
"""

create_modules_table = """
CREATE TABLE IF NOT EXISTS modules (
    module_id INT AUTO_INCREMENT PRIMARY KEY,
    courseid VARCHAR(150) NOT NULL,
    title VARCHAR(255) NOT NULL,
    learning_points TEXT,
    FOREIGN KEY (courseid) REFERENCES coursedetails(courseid) ON DELETE CASCADE
);
"""

create_lessons_table = """
CREATE TABLE IF NOT EXISTS lessons (
    lesson_id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE CASCADE
);
"""

create_quizzes_table = """
CREATE TABLE IF NOT EXISTS quizzes (
    quiz_id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE CASCADE
);
"""

create_user_courses_table = """
CREATE TABLE IF NOT EXISTS user_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) NOT NULL,
    courseid VARCHAR(150) NOT NULL,
    status ENUM('enrolled', 'completed') DEFAULT NULL,
    progress_percentage FLOAT DEFAULT 0,
    FOREIGN KEY (courseid) REFERENCES coursedetails(courseid) ON DELETE CASCADE
);
"""

create_user_lesson_progress_table = """
CREATE TABLE IF NOT EXISTS user_lesson_progress (
    email VARCHAR(150) NOT NULL,
    lesson_id INT NOT NULL,
    completion_status ENUM('not started', 'in progress', 'completed') DEFAULT 'not started',
    PRIMARY KEY (email, lesson_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE
);
"""

create_user_quiz_scores_table = """
CREATE TABLE IF NOT EXISTS user_quiz_scores (
    email VARCHAR(150) NOT NULL,
    quiz_id INT NOT NULL,
    score INT,
    total_score INT,
    pass_fail_status ENUM('pass', 'fail'),
    attempt_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (email, quiz_id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE
);
"""

create_progress_visualization_table = """
CREATE TABLE IF NOT EXISTS progress_visualization (
    email VARCHAR(150) NOT NULL,
    courseid VARCHAR(150) NOT NULL,
    course_progress_percentage FLOAT DEFAULT 0,
    total_quizzes INT DEFAULT 0,
    quizzes_passed INT DEFAULT 0,
    quizzes_failed INT DEFAULT 0,
    total_modules INT DEFAULT 0,
    modules_completed INT DEFAULT 0,
    PRIMARY KEY (email, courseid),
    FOREIGN KEY (courseid) REFERENCES coursedetails(courseid) ON DELETE CASCADE
);
"""

create_quiz_questions_table = """
CREATE TABLE IF NOT EXISTS quiz_questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    question_text TEXT NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE
);
"""

create_quiz_options_table = """
CREATE TABLE IF NOT EXISTS quiz_options (
    option_id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES quiz_questions(question_id) ON DELETE CASCADE
);
"""

create_user_module_progress_table = """
CREATE TABLE IF NOT EXISTS user_module_progress (
    email VARCHAR(150) NOT NULL,
    module_id INT NOT NULL,
    progress_percentage FLOAT DEFAULT 0,
    completion_status ENUM('not started', 'in progress', 'completed') DEFAULT 'not started',
    PRIMARY KEY (email, module_id),
    FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE CASCADE
);
"""

table_creation_queries = [
    create_coursedetails_table,
    create_modules_table,
    create_lessons_table,
    create_quizzes_table,
    create_user_courses_table,
    create_user_module_progress_table,
    create_user_lesson_progress_table,
    create_user_quiz_scores_table,
    create_progress_visualization_table,
    create_quiz_questions_table,
    create_quiz_options_table
]
def create_tables():
    connection = None
    try:
        connection = get_db_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS UpSkill_5;")
            print("Database UpSkill_5 created or already exists.")
            connection.database = "UpSkill_5"
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
        
