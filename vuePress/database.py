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
        if (self.getRegister('admin') is None):
            registerDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            hashedSaltedPasswd = hashlib.pbkdf2_hmac('sha256', "Dmiip2025".encode(), registerDate.encode(), 10, 64).hex()  # 10 is the iteratin count
            email = "fdudmiip@163.com"
            self.exec("INSERT INTO users (username, passwd, role, register, email) VALUES (?, ?, ?, ?, ?)", ("admin", hashedSaltedPasswd, "admin", registerDate, email))
        self.nances = dict()
    
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
        for nance, generateTime in self.nances.items():
            if ((datetime.now() - generateTime).total_seconds() > 30):
                self.nances.pop(nance)
    
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
        
    def addUser(self, username, hashedSaltedPasswd, role, registerDate, email="N/A"):
        if (self.getRegister(username)):
            return False  # already exists someone with the same username
        self.exec("INSERT INTO users (username, passwd, role, register, email) VALUES (?, ?, ?, ?, ?)", (username, hashedSaltedPasswd, role, registerDate, email))
        return True
    
    def getUser(self, username):
        user = self.exec("SELECT role, register, email FROM users WHERE username = ?", (username, ), "one")
        return user

    def getAllUser(self):
        users = self.exec("SELECT username, role, register, email FROM users", getResult="all")
        userList = list()
        for user in users:
            userList.append({
                "username": user[0],
                "role": user[1],
                "register": user[2],
                "email": user[3]
            })
        return userList