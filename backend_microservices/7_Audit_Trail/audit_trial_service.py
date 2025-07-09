from flask import Flask, jsonify
from create_tables import create_tables
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_connection import get_db_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
create_tables()
@app.route('/api/audit_trial/', methods=['GET', 'POST'])
def student_course():
    return jsonify({"message": "Audit Trail service is working!"})

@app.route('/api/audit_trial/fetch-audit', methods=["GET"])
def fetch_audit():
    connection = get_db_connection()
    connection.database = "UpSkill_7"
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM audit_trail")
    audit_details = cursor.fetchall()
    return jsonify({"message":"Audit details fetch successful", "content":audit_details})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
