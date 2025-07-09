import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, jsonify

app = Flask(__name__)




@app.route('/api/sending_notifications/', methods=['GET', 'POST'])
def sending_notifications():
    return jsonify({"message": "Sending Notifications service is working!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
