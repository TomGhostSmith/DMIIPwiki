from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Allow frontend to send cookies

# Define a simple username & password (For a real app, use a database!)
USER_CREDENTIALS = {
    "admin": "123",
    "tom": "123"
}
admins = {"admin"}

# Token expiration time (1 hour)
EXPIRATION_TIME = 3600  # seconds

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Check credentials
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        role = 'admin' if username in admins else 'user'
        response = make_response(jsonify({"role": role}))
        response.set_cookie("auth_token", role, httponly=True, max_age=EXPIRATION_TIME)
        return response
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    auth_token = request.cookies.get("auth_token")
    if auth_token == 'admin' or auth_token == 'user':
        return jsonify({"role": auth_token})
    return jsonify({"role": 'logout'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logged out"}))
    response.set_cookie("auth_token", "", expires=0)  # Delete cookie
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9006, debug=True)
