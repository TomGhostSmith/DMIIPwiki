from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import time
import os
import hashlib
from database import Database

db = Database("wiki.db")
app = Flask(__name__)
# CORS(app, supports_credentials=True, origins=["http://10.138.42.155"])  # Allow frontend to send cookies
CORS(app, supports_credentials=True)  # Allow frontend to send cookies

def sendEmail(receive, subject, content):
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    smptServer = 'smtp.163.com'
    user = 'fdudmiip@163.com'
    password = 'CYkaC37sRSGnGKwG'
    sender = "fdudmiip@163.com"

    # msg = MIMEText(content,'html','utf-8')
    msg = MIMEText(content,'plain','utf-8')
    msg["Subject"] = Header(subject,'utf-8')
    msg['From'] = sender
    if (isinstance(receive, list)):
        msg['To'] = ';'.join(receive)
    else:
        msg['To'] = receive

    smtp=smtplib.SMTP_SSL(smptServer,465)
    smtp.helo(smptServer)
    smtp.ehlo(smptServer)
    smtp.login(user,password)
    smtp.sendmail(sender, receive, msg.as_string())
    smtp.quit()
    print("Mail sent successfully")

def calculate_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):  # Read in 4KB chunks
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

# Token expiration time (1 hour)
EXPIRATION_TIME = 3600  # seconds

@app.route('/getNance', methods=['POST'])
def getNance():
    data = request.json
    username = data.get("username")
    salt = db.getRegister(username)
    if salt is not None:
        nance = db.getNance()
        return jsonify({"salt": salt, "nance": nance})
    else:
        return jsonify({"salt": None, "nance": None}), 401

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    nance = data.get("nance")
    if db.checkUser(username, password, nance):
        role = db.getRole(username)
        response = make_response(jsonify({"user": username, "role": role}))
        response.set_cookie("user_name", username, httponly=True, max_age=EXPIRATION_TIME)
        return response
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/check-auth', methods=['GET'])
def check_auth():
    userName = request.cookies.get("user_name")
    role = db.getRole(userName)
    if role == 'admin' or role == 'user':
        return jsonify({"user": userName, "role": role})
    return jsonify({"user": "", "role": 'logout'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logged out"}))
    response.set_cookie("user_name", "", expires=0)  # Delete cookie
    return response

@app.route('/loadContent', methods=["POST"])
def getContent():
    data = request.json
    fileName = data.get("fileName")
    if (os.path.exists(fileName)):
        attrs = dict()
        h = calculate_md5(fileName)
        attrs['md5'] = h
        stage = 0
        with open(fileName, encoding='utf-8') as fp:
            content = ""
            for line in fp.readlines():
                if line.strip() == "---":
                    stage += 1
                elif stage == 1:
                    if (line.strip()):
                        key = line[:line.find(":")].strip()
                        value = line[line.find(":") + 1 : ].strip()
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
    if (os.path.exists(fileName)):
        md5 = attrs.get("md5")
        h = calculate_md5(fileName)
        if md5 != h:
            return jsonify({"resp": "modified"}), 409

    baseFolder = os.path.dirname(fileName)
    os.makedirs(baseFolder, exist_ok=True)

    with open(fileName, 'wt', encoding='utf-8') as fp:
        fp.write("---\n")
        for key, value in attrs.items():
            if key == "md5":
                continue
            fp.write(f"{key}: {value}\n")
        fp.write("---\n")
        # fp.write(f"# {attrs["title"]}\n")
        fp.write(content)
        os.system("bash build.sh")
    return jsonify({"resp": "ok"})

@app.route("/getAllUser", methods=["GET"])
def getAllUser():
    userName = request.cookies.get("user_name")
    role = db.getRole(userName)
    if role != "admin":
        return jsonify([]), 401
    return jsonify({"data": db.getAllUser()})

@app.route('/addUser', methods=['POST'])
def addUser():
    if db.getRole(request.cookies.get("user_name")) != "admin":
        return jsonify({'error': 'unauthorized'}), 401
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    email = data.get("email")
    if (email is None or email == ""):
        email = "N/A"
    register = data.get("register")
    if (not db.checkUserName(username)):
        return jsonify({'error': 'username exists'}), 400
    db.addUser(username, password, role, register, email)
    return jsonify({})


@app.route('/getUserInfo', methods=["GET"])
def getUserInfo():
    userName = request.cookies.get("user_name")
    user = db.getUser(userName)
    if user is None:
        return jsonify({"user": "", "role": 'logout'}), 401
    else:
        return jsonify({"user": userName, "role": user[0], "registerDate": user[1], "email": user[2]})

if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=9006, ssl_context=('/Data/GhoST/ssl.crt', '/Data/GhoST/ssl.key'))
    # sendEmail(["24110850013@m.fudan.edu.cn", "20307110008@fudan.edu.cn"], "Email test", "This is a email test")
    app.run(host="0.0.0.0", port=9006)
