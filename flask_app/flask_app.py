import sys
import os

# Get the project directory (one level up from the current script's directory)
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the project directory to the sys.path
sys.path.insert(0, project_dir)

from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
from config.config import flask_port_no

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)


@app.route('/', methods=['GET'])
def index():
    return "Discord-TWS Flask server running"

        
# Test General channel
@app.route('/1088950623883513970/1088950623883513973/latest-messages', methods=["GET", "POST"])
def post_and_get_message_data_from_Test_General_channel():
    global test_data 
    if request.method == "POST": 
        test_data = request.json
        return jsonify(test_data)
    else:
        print(test_data)
        return jsonify(test_data)

# Test second-channel channel
@app.route('/1088950623883513970/1112133199351521290/latest-messages', methods=["GET", "POST"])
def post_and_get_message_data_from_Test_second_channel():
    global test_data2 
    if request.method == "POST": 
        test_data2 = request.json
        return jsonify(test_data2)
    else:
        print(test_data2)
        return jsonify(test_data2)
    
# Discord Analyst1 channel
@app.route('/697936741117460640/1035245170582626334/latest-messages', methods=["GET", "POST"])
def post_and_get_message_data_from_OOT_Analyst1_channel():
    global Analyst1_data 
    if request.method == "POST": 
        Analyst1_data = request.json
        return jsonify(Analyst1_data)
    else:
        print(Analyst1_data)
        return jsonify(Analyst1_data)
    
# Discord Analyst2 channel
@app.route('/697936741117460640/1025803258691862678/latest-messages', methods=["GET", "POST"])
def post_and_get_message_data_from_OOT_Analyst2_channel():
    global Analyst2_data 
    if request.method == "POST": 
        Analyst2_data = request.json
        return jsonify(Analyst2_data)
    else:
        print(Analyst2_data)
        return jsonify(Analyst2_data)
    
# Discord Analyst3 channel
@app.route('/697936741117460640/1139560883127857304/latest-messages', methods=["GET", "POST"])
def post_and_get_message_data_from_OOT_Analyst3_channel():
    global Analyst3_data 
    if request.method == "POST": 
        Analyst3_data = request.json
        return jsonify(Analyst3_data)
    else:
        print(Analyst3_data)
        return jsonify(Analyst3_data)
    
# Discord Analyst4 channel
@app.route('/697936741117460640/782068070977110027/latest-messages', methods=["GET", "POST"])
def post_and_get_message_data_from_OOT_Analyst4_channel():
    global Analyst4_data
    if request.method == "POST": 
        Analyst4_data = request.json
        return jsonify(Analyst4_data)
    else:
        print(Analyst4_data)
        return jsonify(Analyst4_data)
    
    
if __name__ == '__main__':
    test_data = []
    test_data2 = []
    Analyst1_data = []
    Analyst2_data = []
    Analyst3_data = []
    Analyst4_data = []
    app.run(host='127.0.0.1', port=flask_port_no())