from flask import Flask, request, jsonify, make_response, send_file, send_from_directory
from flask_cors import CORS
import time
import os
import hashlib
import shutil
from datetime import datetime

from database import Database

db = Database("wiki.db")
app = Flask(__name__)
app.config['IMAGE_FOLDER'] = "./resources"
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

    msg = MIMEText(content,'html','utf-8')
    # msg = MIMEText(content,'plain','utf-8')
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
EXPIRATION_TIME = 3600 * 7 * 24  # seconds
# EXPIRATION_TIME = 600  # seconds

@app.route('/getNance', methods=['POST'])
def getNance():
    data = request.json
    username = data.get("username")
    print(username)
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
    if (db.checkUser(username, password, nance)):
        role = db.getRole(username)
        user = db.getUser(username)
        response = make_response(jsonify({"user": username, "role": role, "emptyEmail": user[2] == ""}))
        response.set_cookie("user_name", username, httponly=True, max_age=EXPIRATION_TIME)
        # if (user[2] == ""):
        #     return response
        # else:
        #     return response
        return response
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/check-auth', methods=['GET'])
def check_auth():
    userName = request.cookies.get("user_name")
    role = db.getRole(userName)
    if role == 'admin' or role == 'user':
        response = make_response(jsonify({"user": userName, "role": role}))
        response.set_cookie("user_name", userName, httponly=True, max_age=EXPIRATION_TIME)
        return response
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
        attrs, content = getMarkdownContent(fileName)
        return jsonify({"content": content, "attrs": attrs})
    else: 
        return jsonify({"content": "", "attrs": {}}), 404
        # return jsonify({"error": "file not exists"}), 404

def getMarkdownContent(fileName):
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
    return attrs, content

def getHistoryFolder(originFileName):
    return f"./history/{originFileName}".replace(".md", "")

def getHistoryFileName(modifyDate):
    return f"{modifyDate.replace(' ', "_").replace(':', ";").replace("+", ",")}.md"

def extractModifyDate(fileName):
    return fileName.replace(".md", "").replace("_", " ").replace(";", ":").replace(",", "+")

def extractMarkdownHeader(fileName):
    attrs = dict()
    stage = 0
    with open(fileName, encoding='utf-8') as fp:
        for line in fp.readlines():
            if line.strip() == "---":
                stage += 1
            elif stage == 1:
                if (line.strip()):
                    key = line[:line.find(":")].strip()
                    value = line[line.find(":") + 1 : ].strip()
                    attrs[key] = value
            else:
                break
    return attrs

@app.route('/saveContent', methods=["POST"])
def saveContent():
    data = request.json
    fileName = data.get("fileName")
    content = data.get("content")
    attrs = data.get("attrs")

    # move origin file to history folder

    if (os.path.exists(fileName)):
        historyFolder = getHistoryFolder(fileName)
        os.makedirs(historyFolder, exist_ok=True)
        md5 = attrs.get("md5")
        h = calculate_md5(fileName)
        if md5 != h:
            return jsonify({"resp": "modified"}), 409
        oldAttrs = extractMarkdownHeader(fileName)
        historyName = f"{historyFolder}/{getHistoryFileName(oldAttrs["lastModifyDate"])}"
        shutil.copy(fileName, historyName)
        db.movePage(fileName, oldAttrs["lastModifyDate"], historyName)

    baseFolder = os.path.dirname(fileName)
    os.makedirs(baseFolder, exist_ok=True)
    # write to new file
    with open(fileName, 'wt', encoding='utf-8') as fp:
        fp.write("---\n")
        for key, value in attrs.items():
            if key == "md5":
                continue
            fp.write(f"{key}: {value}\n")
        fp.write("---\n")
        # fp.write(f"# {attrs["title"]}\n")
        fp.write(content)
        db.updatePage(fileName, attrs["lastModifyDate"], attrs["lastModify"])
    os.system("bash build.sh")  # close the file first, then build
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
        return jsonify({"error": "没有权限"}), 401
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    email = data.get("email")
    if (email is None or email == ""):
        email = "N/A"
    resp = db.addUser(username, role, email)
    if (not resp):
        return jsonify({'error': '用户名已存在'}), 400
    return jsonify({})

@app.route('/modifyUser', methods=["PUT"])
def modifyUser():
    if db.getRole(request.cookies.get("user_name")) != "admin":
        return jsonify({"error": "没有权限"}), 401
    data = request.json
    username = data.get("username")
    role = data.get("role")
    email = data.get("email")
    if (email is None or email == ""):
        email = "N/A"
    if (db.checkUserName(username)):
        return jsonify({'error': '不存在该用户'}), 400
    db.updateUser(username, role, email)
    return jsonify({})


@app.route('/getUserInfo', methods=["POST"])
def getUserInfo():
    cookieUserName = request.cookies.get("user_name")
    data = request.json
    userName = data.get('username')
    if (cookieUserName != "admin" and cookieUserName != userName):
        return jsonify({"error": "没有权限"}), 401
    user = db.getUser(userName)
    if user is None:
        return jsonify({"error": "没有权限"}), 401
    else:
        return jsonify({"user": userName, "role": user[0], "registerDate": user[1], "email": user[2]})

@app.route('/deleteUser', methods=['POST'])
def deleteUser():
    cookieUserName = request.cookies.get("user_name")
    data = request.json
    userName = data.get('username')
    if (cookieUserName != "admin"):
        return jsonify({"error": "没有权限"}), 401
    resp = db.deleteUser(userName)
    if (not resp):
        return jsonify({"error": "不存在该用户"}), 404
    else:
        return jsonify({})
    
@app.route('/resetPasswd', methods=['PUT'])
def resetPasswd():
    cookieUserName = request.cookies.get("user_name")
    data = request.json
    userName = data.get('username')
    if (cookieUserName != "admin"):
        return jsonify({"error": "没有权限"}), 401
    resp = db.resetPassword(userName)
    if (not resp):
        return jsonify({"error": "不存在该用户"}), 404
    else:
        return jsonify({})
    
@app.route('/modifyPasswd', methods=['PUT'])
def modifyPasswd():
    cookieUserName = request.cookies.get("user_name")
    data = request.json
    userName = data.get('username')
    oldPasswd = data.get('oldPasswd')
    passwd = data.get('passwd')
    nance = data.get('nance')
    if (cookieUserName != userName):
        return jsonify({"error": "没有权限"}), 401
    if not db.checkUser(userName, oldPasswd, nance):
        return jsonify({"error": "旧密码错误"}), 400
    resp = db.modifyPassword(userName, passwd)
    if (not resp):
        return jsonify({"user": "", "role": 'logout'}), 404
    else:
        return jsonify({})

@app.route('/getPageHistory', methods=['POST'])
def getHistory():
    data = request.json
    fileName = data.get('file')
    histories = db.getPageHistory(fileName)
    currentVersion = db.getPageCurrentVersion(fileName)
    return jsonify({"data": list(reversed(histories)), "currentVersion": currentVersion})

@app.route('/getHistoryPage', methods=["POST"])
def getHistoryPage():
    data = request.json
    fileName = data.get('file')
    modifyDate = data.get('time')
    filePath = db.getPagePath(fileName, modifyDate)
    attrs, content = getMarkdownContent(filePath)
    return jsonify({"content": content, "attrs": attrs})

@app.route('/forgetPass', methods=["POST"])
def forgetPass():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    user = db.getUser(username)
    if (user is None or user[2]!= email or email == ""):
        return jsonify({"error": "用户名或邮箱错误"}), 404
    
    code = db.getCode()
    emailText = f'<p>尊敬的 DMIIP wiki 用户您好：</p>' + \
    "<p>我们收到了您发起的密码重置请求，以下是您本次操作所需的验证码：</p><br>" + \
    f"<h1>{code}</h1><br>" + \
    "<p>请注意：</p>" + \
    "<p>1. 本验证码有效期为10分钟</p>" + \
    "<p>2. 请在密码重置页面输入此验证码继续后续操作</p>" + \
    "<p>3. 如非本人操作，请忽略本邮件</p><br><hr><br>" + \
    "<p>安全提示：我们的工作人员不会通过任何方式向您索要验证码，请注意保护账户信息安全。</p><br>" + \
    "<p>如有疑问，请联系邮箱：fdudmiip@163.com</p>" + \
    "<p>感谢您对DMIIP wiki的支持</p><br>" + \
    "<p>DMIIP wiki 开发组 敬上</p>"
    # print(emailText)
    sendEmail([email], "【DMIIP wiki】密码重置验证码", emailText)
    return jsonify({})

@app.route('/modifyPasswdFromEmail', methods=['PUT'])
def modifyPasswdFromEmail():
    data = request.json
    userName = data.get('username')
    passwd = data.get('passwd')
    code = data.get('code')
    if not db.checkCode(code):
        return jsonify({"error": "验证码错误"}), 400
    resp = db.modifyPassword(userName, passwd)
    if (not resp):
        return jsonify({"user": "", "role": 'logout'}), 404
    else:
        return jsonify({})
    
def getLocalPath(fileName, uploadDate):
    baseFolder = "./upload"
    return f"{baseFolder}/{fileName}-{uploadDate}"

def receiveFile():
    thisTime = datetime.now()
    uploadDate = thisTime.strftime('%Y-%m-%d %H:%M:%S')
    fileDate = thisTime.strftime('%Y%m%d%H%M%S')
    if 'file' not in request.files:
        return None
    # files = request.files.getlist('files')
    file = request.files["file"]
    fileName = file.filename
    filePath = getLocalPath(fileName, fileDate)
    file.save(filePath)
    md5 = calculate_md5(filePath)
    fileSize = os.path.getsize(filePath)
    return fileName, filePath, md5, fileSize, uploadDate

def getUploadDate(uploadDate, localFilePath=None):
    # fileName = os.path.basename(localFilePath)
    # uploadDate = fileName[fileName.rfind("-") + 1:]
    # return uploadDate
    return uploadDate.replace("-", "").replace(":", "").replace(' ', "")



# netdisk part
@app.route('/uploadFile', methods=["POST"])
def uploadFile():
    cookieUserName = request.cookies.get("user_name")
    username = request.form.get('user')
    scope = request.form.get('scope')
    # print(f"{cookieUserName}, {username}")
    if (cookieUserName != username):
        return jsonify({"error": "没有权限"}), 401
    resp = receiveFile()
    if (not resp):
        return jsonify({"error": "未知错误"}), 400
    fileName, filePath, md5, fileSize, uploadDate = resp
    id = db.uploadFile(fileName, uploadDate, username, fileSize, md5, filePath, scope)
    return jsonify({"id": id})

@app.route('/reUploadFile', methods=["PUT"])
def reUploadFile():
    cookieUserName = request.cookies.get("user_name")
    scope = request.form.get('scope')
    id = int(request.form.get('id'))
    file = db.getFileByID(id)
    if (file is None):
        return jsonify({"error": "文件不存在"}), 404
    if (cookieUserName != file["uploadUser"]):
        return jsonify({"error": "没有权限"}), 401
    fileName, filePath, md5, fileSize, uploadDate = receiveFile()
    db.reUploadFile(id, fileName, uploadDate, fileSize, md5, filePath, scope)
    os.remove(file["localPath"])
    return jsonify({})

@app.route('/getLabFiles', methods=["GET"])
def getPublicFiles():
    cookieUserName = request.cookies.get("user_name")
    role = db.getRole(cookieUserName)
    if (role == "logout"):
        return jsonify({"error": "没有权限"}), 401
    files = db.getLabFiles()
    return jsonify({"data": files})

@app.route("/deleteFile/<file_id>", methods=["DELETE"])
def  deleteFile(file_id):
    id = int(file_id)
    file = db.getFileByID(id)
    cookieUserName = request.cookies.get("user_name")
    if (file is None):
        return jsonify({"error": "文件不存在"}), 404
    if (cookieUserName != file["uploadUser"]):
        return jsonify({"error": "没有权限"}), 401
    if (os.path.exists(file["localPath"])):
        os.remove(file["localPath"])
    db.deleteFile(id)
    return jsonify({})

@app.route('/updateFileMeta', methods=["PUT"])
def updateFileMeta():
    cookieUserName = request.cookies.get("user_name")
    data = request.json
    id = int(data.get('id'))
    fileName = data.get('fileName')
    scope = data.get('scope')
    file = db.getFileByID(id)
    if (file is None):
        return jsonify({"error": "文件不存在"}), 404
    if (cookieUserName != file["uploadUser"]):
        return jsonify({"error": "没有权限"}), 401
    uploadDate = getUploadDate(file["uploadDate"])
    newLocalPath = getLocalPath(fileName, uploadDate)
    if (newLocalPath != file["localPath"]):
        shutil.move(file["localPath"], newLocalPath)
    db.updateFileMeta(id, fileName, newLocalPath, scope)
    return jsonify({})

@app.route('/getFileInfo', methods=["POST"])
def getFileInfo():
    cookieUserName = request.cookies.get("user_name")
    data = request.json
    id = int(data.get('id'))
    file = db.getFileByID(id)
    if (file is None):
        return jsonify({"error": "文件不存在"}), 404
    if (cookieUserName != file["uploadUser"] and file["scope"] == "private"):
        return jsonify({"error": "没有权限"}), 401
    if (cookieUserName is None and file["scope"] == "lab"):
        return jsonify({"error": "没有权限"}), 401
    return jsonify({"file": file})
    
@app.route('/downloadFile/<file_id>', methods=["GET"])
def downloadFile(file_id):
    id = int(file_id)
    cookieUserName = request.cookies.get("user_name")
    file = db.getFileByID(id)
    if file is None:
        return jsonify({"error": "文件不存在"}), 404
    if (cookieUserName != file["uploadUser"] and file["scope"] == "private"):
        return jsonify({"error": "没有权限"}), 401
    if (cookieUserName is None and file["scope"] == "lab"):
        return jsonify({"error": "没有权限"}), 401
    
    return send_file(file["localPath"], as_attachment=True, download_name=file["fileName"])

@app.route('/getImages', methods=["GET"])
def getImages():
    try:
        # List all image files in the image folder
        images = [f for f in os.listdir(app.config['IMAGE_FOLDER'] + "/dashboard") if f.endswith(('jpg', 'jpeg', 'png', 'gif'))]
        image_urls = [f'/api/dashboardImages/{image}' for image in images]  # Build URLs for images
        return jsonify({'images': image_urls})  # Return as JSON
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboardImages/<filename>', methods=['GET'])
def get_dashboard_image(filename):
    try:
        return send_from_directory(app.config['IMAGE_FOLDER'] + "/dashboard", filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    
@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    try:
        return send_from_directory(app.config['IMAGE_FOLDER'], filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=9006, ssl_context=('/Data/GhoST/ssl.crt', '/Data/GhoST/ssl.key'))
    # sendEmail(["24110850013@m.fudan.edu.cn", "20307110008@fudan.edu.cn"], "Email test", "This is a email test")
    app.run(host="0.0.0.0", port=9006)
