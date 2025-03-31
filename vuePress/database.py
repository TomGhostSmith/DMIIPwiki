import os
import sqlite3
import hashlib
import random
from datetime import datetime

class Database():
    def __init__(self, file):
        self.file = file
        sql = '''
                       CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY NOT NULL,
                        passwd TEXT NOT NULL,
                        role TEXT NOT NULL,
                        register TEXT NOT NULL,
                        email TEXT NOT NULL
                       )
                       '''
        self.exec(sql)
        sql = '''
                       CREATE TABLE IF NOT EXISTS docs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        modifydate TEXT NOT NULL,
                        modifyuser TEXT NOT NULL,
                        filepath TEXT NOT NULL
                       )
                       '''
        self.exec(sql)
        if (self.getRegister('admin') is None):
            email = "fdudmiip@163.com"
            self.addUser("admin", "admin", email)
        self.nances = dict()
        self.codes = dict()
    
    def exec(self, sql, param=(), getResult=None):
        conn = sqlite3.connect(self.file)
        cursor = conn.cursor()
        try:
            cursor.execute(sql, param)
            result = None
            if (getResult == "one"):
                result = cursor.fetchone()
            elif (getResult == "all"):
                result = cursor.fetchall()
            conn.commit()
        except Exception as e:
            print(e)
            result = False
        finally:
            conn.close()
        return result

    def getRegister(self, userName):
        res = self.exec('SELECT register FROM users WHERE username = ?', (userName, ), "one")
        if res is not None:
            res = res[0]
        return res
    
    def cleanExpiredNance(self):
        for nance, generateTime in list(self.nances.items())[:]:
            if ((datetime.now() - generateTime).total_seconds() > 30):
                self.nances.pop(nance)

    def cleanExpiredCode(self):
        for code, generateTime in list(self.codes.items())[:]:
            if ((datetime.now() - generateTime).total_seconds() > 600):
                self.codes.pop(code)
    
    def getRole(self, userName):
        res = self.exec('SELECT role FROM users WHERE username = ?', (userName, ), "one")
        if res is not None:
            res = res[0]
        else:
            res = "logout"
        return res
    
    def getNance(self):
        nance = str(random.random())
        self.nances[nance] = datetime.now()
        return nance

    def getCode(self):
        code = f"{random.random():.6f}"[2:8]
        self.codes[code] = datetime.now()
        return code
    
    def checkCode(self, code):
        self.cleanExpiredCode()
        res = code in self.codes
        if (res):
            self.codes.pop(code)
        return res

    def checkUser(self, userName, givenPasswd:str, nance:str):
        self.cleanExpiredNance()
        if (nance not in self.nances):
            return False
        self.nances.pop(nance)
        hashedSaltedPasswd:str = self.exec('SELECT passwd FROM users WHERE username = ?', (userName, ), "one")
        if (hashedSaltedPasswd is None):
            return false
        hashedSaltedPasswd = hashedSaltedPasswd[0]
        if (hashedSaltedPasswd is None):
            return False
        targetPasswd = hashlib.pbkdf2_hmac('sha256', hashedSaltedPasswd.encode(), nance.encode(), 10, 64).hex()  # 10 is the iteratin count
        return (targetPasswd == givenPasswd)
    
    def checkUserName(self, username):
        if (self.getRegister(username)):
            return False  # already exists someone with the same username
        return True
        
    def addUser(self, username, role, email="N/A"):
        if (self.getRegister(username)):
            return False  # already exists someone with the same username
        registerDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.exec("INSERT INTO users (username, passwd, role, register, email) VALUES (?, ?, ?, ?, ?)", (username, "pw", role, registerDate, email))
        self.resetPassword(username)
        return True
    
    def updateUser(self, username, role, email="N/A"):
        if (not self.getRegister(username)):
            return False  # user not exists
        self.exec("UPDATE users SET role = ?, email = ? WHERE username = ?", (role, email, username))
        return True
    
    def getUser(self, username):
        user = self.exec("SELECT role, register, email FROM users WHERE username = ?", (username, ), "one")
        if user is not None:
            return [
                user[0],
                user[1],
                user[2] if user[2] != 'N/A' else ""
            ]
        else:
            return None

    def getAllUser(self):
        users = self.exec("SELECT username, role, register, email FROM users", getResult="all")
        userList = list()
        for user in users:
            userList.append({
                "username": user[0],
                "role": user[1],
                "register": user[2],
                "email": user[3] if user[3] != "N/A" else ""
            })
        return userList
    
    def deleteUser(self, username):
        if (self.checkUserName(username)):
            return False  # user not exists
        self.exec("DELETE FROM users WHERE username = ?", (username, ))
        return True

    def resetPassword(self, username):
        if (self.checkUserName(username)):
            return False  # user not exists
        
        passwd = f"Dmiip{datetime.now().strftime('%Y')}"
        register = self.getRegister(username)
        hashedSaltedPasswd = hashlib.pbkdf2_hmac('sha256', passwd.encode(), register.encode(), 10, 64).hex()  # 10 is the iteratin count
        self.exec("UPDATE users SET passwd = ? WHERE username = ?", (hashedSaltedPasswd, username))
        return True
    
    def modifyPassword(self, username, hashedSaltedPasswd):
        if (self.checkUserName(username)):
            return False  # user not exists
        self.exec("UPDATE users SET passwd = ? WHERE username = ?", (hashedSaltedPasswd, username))
        return True
    
    def getFileHistory(self, fileName):
        results = self.exec("SELECT modifyuser, modifydate FROM docs WHERE filename = ?", (fileName, ), "all")
        if results is None:
            results = list()
        res = list()
        for history in results:
            res.append({
                "user": history[0],
                "time": history[1]
            })
        return res

    def getFilePath(self, fileName, modifyDate):
        result = self.exec("SELECT filepath FROM docs WHERE filename = ? AND modifydate = ?", (fileName, modifyDate), "one")
        if result is None:
            return None
        return result[0]

    def moveFile(self, fileName, modifyDate, fileNewPath):
        if (not self.getFilePath(fileName, modifyDate)):
            return False
        self.exec("UPDATE docs SET filepath = ? WHERE filename = ? AND modifydate = ?", (fileNewPath, fileName, modifyDate))
        return True

    def updateFile(self, fileName, modifyDate, modifyUser):
        if (self.getFilePath(fileName, modifyDate)):
            return False
        self.exec("INSERT INTO docs (filename, modifydate, modifyuser, filepath) VALUES (?, ?, ?, ?)", (fileName, modifyDate, modifyUser, fileName))
        return True
    
    def getCurrentVersion(self, fileName):
        result = self.exec("SELECT modifydate FROM docs WHERE filename = ? AND filepath = ?", (fileName, fileName), "one")
        if result is None:
            return None
        return result[0]