from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import time
import os

app = Flask(__name__)
# CORS(app, supports_credentials=True, origins=["http://10.138.42.155"])  # Allow frontend to send cookies
CORS(app, supports_credentials=True)  # Allow frontend to send cookies

# Define a simple username & password (For a real app, use a database!)
USER_CREDENTIALS = {
    "admin": "123",
    "tom": "123"
}
admins = {"admin"}

# Token expiration time (1 hour)
EXPIRATION_TIME = 3600  # seconds

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Check credentials
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        role = 'admin' if username in admins else 'user'
        response = make_response(jsonify({"role": role}))
        # response.set_cookie("auth_token", role, httponly=True, secure=True, samesite=None, max_age=EXPIRATION_TIME)
        response.set_cookie("auth_token", role, httponly=True, max_age=EXPIRATION_TIME)
        # response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/check-auth', methods=['GET'])
def check_auth():
    auth_token = request.cookies.get("auth_token")
    if auth_token == 'admin' or auth_token == 'user':
        return jsonify({"role": auth_token})
    return jsonify({"role": 'logout'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logged out"}))
    response.set_cookie("auth_token", "", expires=0)  # Delete cookie
    return response

@app.route('/loadContent', methods=["POST"])
def getContent():
    data = request.json
    fileName = data.get("fileName")
    if (os.path.exists(fileName)):
        attrs = dict()
        stage = 0
        with open(fileName, encoding='utf-8') as fp:
            content = ""
            for line in fp.readlines():
                if line.strip() == "---":
                    stage += 1
                elif stage == 1:
                    if (line.strip()):
                        key = line[:line.find(":")].strip()
                        value = line[line.find(":")+1 : ].strip()
                        attrs[key] = value
                # elif stage == 2:
                #     if (line.strip()):
                #         stage += 1
                #         if (not line.startswith("# ")):
                #             content += line
                else:
                    content += line
        return jsonify({"content": content, "attrs": attrs, "md5": ""})
    else: 
        return jsonify({"content": "", "attrs": attrs, "md5": ""})
        # return jsonify({"error": "file not exists"}), 404
    
@app.route('/saveContent', methods=["POST"])
def saveContent():
    data = request.json
    fileName = data.get("fileName")
    content = data.get("content")
    attrs = data.get("attrs")
    md5 = data.get("md5")
    if (os.path.exists(fileName)):
        # TODO: check md5


        with open(fileName, 'wt', encoding='utf-8') as fp:
            fp.write("---\n")
            for key, value in attrs.items():
                fp.write(f"{key}: {value}\n")
            fp.write("---\n")
            # fp.write(f"# {attrs["title"]}\n")
            fp.write(content)
            os.system("bash build.sh")
        return jsonify({"resp": "ok"})
    else: 
        return jsonify({"error": "file not exists"}), 404

if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=9006, ssl_context=('/Data/GhoST/ssl.crt', '/Data/GhoST/ssl.key'))
    app.run(host="0.0.0.0", port=9006)
