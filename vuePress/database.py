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
        finally:
            conn.close()
        return result

    def getSalt(self, userName):
        return self.exec('SELECT register FROM users WHERE username = ?', (userName, ), "one")
    
    def getNance(self):
        return str(random.random())

    def checkUser(self, userName, nance, givenPasswd):
        hashedSaltedPasswd:str = self.exec('SELECT register FROM users WHERE username = ?', (userName, ), "one")
        if (hashedSaltedPasswd is None):
            return False
        targetPasswd = hashlib.pbkdf2_hmac('sha256', hashedSaltedPasswd.encode(), nance, 10)  # 10 is the iteratin count
        return (targetPasswd == givenPasswd)
    
    def checkUserName(self, username):
        if (self.getSalt(username)):
            return False  # already exists someone with the same username
        return True
        
    def addUser(self, username, hashedSaltedPasswd, role, registerDate):
        email = "N/A"
        if (self.getSalt(username)):
            return False  # already exists someone with the same username
        self.exec("INSERT INTO users (username, passwd, role, register, email) VALUES (?, ?, ?, ?, ?)", (username, hashedSaltedPasswd, role, registerDate, email))
        return True

        