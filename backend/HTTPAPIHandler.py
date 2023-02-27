from HTTPrequests_refactor import *

import os
import posixpath
import urllib.parse
import mimetypes
import bcrypt
from User import User
from Bulletin import Bulletin
from phonebook import phonebook
from database import session, engine, Base
from datetime import datetime
import sqlalchemy
import json
import jwt

JWT_SECRET = 'IgZCS$!87m3NwtzC'

db = session()
Base.metadata.create_all(engine)

videoMessage = []

class HTTPAPIHandler(HTTPrequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        if directory is None:
            directory = os.getcwd()
        self.directory = os.fspath(directory+ '/../frontend/dist')
        super().__init__(*args, **kwargs)

    def routeHandler(self):
        body = b''

        # TODO
        
        if self.command == 'OPTIONS':
            self.send_response(HTTPStatus.OK)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", self.headers.get('Access-Control-Request-Headers', ' '))
            # self.send_header('Access-Control-Allow-Origin', 'http://10.5.1.158:8080')
            self.send_header('Access-Control-Allow-Origin', 'http://linux1.csie.ntu.edu.twL14443') #
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.send_header('Access-Control-Max-Age', '10')
            self.end_headers()
            return

        match (self.path):
            case "/register":
                body = self.registerHandler()
            case "/login":
                body = self.loginHandler()
            case "/logout":
                body = self.logoutHandler()
            case "/status":
                body = self.statusHandler()
            case "/bulletin":
                body = self.bulletinHandler()
            case "/phonebook":
                body = self.phonebookHandler()
            case _:
                body = self.fileHandler()

        if self.command != 'HEAD' and body:
            if body is not None:
                self.wfile.write(body)

    def jsonResponse(self, status, data, cookies={}):
        data = json.dumps(
            {"success": status == HTTPStatus.OK, "data": data}).encode('utf-8')
        self.send_response(status)
        
        # TODO        
        # self.send_header('Access-Control-Allow-Origin', 'http://10.5.1.158:8080')
        self.send_header('Access-Control-Allow-Origin', 'http://linux1.csie.ntu.edu.tw:14443')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Max-Age', '86400')

        self.send_header("Content-type", 'application/json')
        self.send_header("Content-Length", len(data))
        for key in cookies:
            self.send_header(key, cookies[key])
        self.end_headers()
        return data

    def registerHandler(self): 
        try:
            salt = bcrypt.gensalt()
            hashedPassword = bcrypt.hashpw(
                self.body['password'].encode('utf-8'), salt)
            if (len(self.body['username']) > 0):
                new_user = User(self.body['username'], hashedPassword)
                db.add(new_user)
                db.commit()
            else:
                return self.jsonResponse(HTTPStatus.BAD_REQUEST, "Your username should not be empty.")
        except sqlalchemy.exc.IntegrityError:
            db.rollback()
            return self.jsonResponse(HTTPStatus.BAD_REQUEST, "this username is taken")
        except sqlalchemy.exc.SQLAlchemyError as err:
            db.rollback()
            return self.jsonResponse(HTTPStatus.INTERNAL_SERVER_ERROR, str(err))

        return self.jsonResponse(HTTPStatus.OK, "註冊成功")

    def loginHandler(self):
        result = db.query(User).filter_by(username=self.body['username']).all()
        if len(result) == 0:
            return self.jsonResponse(HTTPStatus.UNAUTHORIZED, "帳號或密碼輸入錯誤")
        else:
            hashpd = result[0].password
        if bcrypt.checkpw((self.body['password']).encode('utf-8'), hashpd):  # success
            encoded_jwt = jwt.encode(
                {'username': self.body['username']}, JWT_SECRET, algorithm='HS256')
            return self.jsonResponse(HTTPStatus.OK, "登入成功", {'Set-Cookie': f'token={encoded_jwt}; SameSite=None; Secure'})
        else:
            return self.jsonResponse(HTTPStatus.UNAUTHORIZED,  "帳號或密碼輸入錯誤")

    def logoutHandler(self):
        return self.jsonResponse(HTTPStatus.OK, "登出成功", {'Set-Cookie': f'token='})
        
    def getSessionData(self):
        cookie = self.headers.get('cookie', '')
        data = {}
        if (cookie != ''):
            try:
                for clause in cookie.split(';'):
                    if (clause.split('=')[0].strip() == 'token'):
                        data = jwt.decode(clause.split('=')[1], JWT_SECRET, algorithms=["HS256"])
            except ( IndexError, jwt.exceptions.DecodeError):
                data = {}
        return data

    def statusHandler(self):
        return self.jsonResponse(HTTPStatus.OK, self.getSessionData())

    def isLoggedIn(self):
        data = self.getSessionData()
        return 'username' in data

    def bulletinHandler(self):
        if self.isLoggedIn():
            if self.command == 'GET':
                results = [row.to_json() for row in db.query(Bulletin).all()]
                return self.jsonResponse(HTTPStatus.OK, list(reversed(results)))
            elif self.command == 'POST':
                try:
                    if (len(self.body['content']) > 2000 or len(self.body['title']) > 200):
                        return self.jsonResponse(HTTPStatus.BAD_REQUEST, "你的字數太多了拉 喜勒靠")
                    new_bulletin = Bulletin(self.getSessionData()['username'], self.body['title'], self.body['content'])
                    db.add(new_bulletin)
                    db.commit()
                    return self.jsonResponse(HTTPStatus.OK, "留言跟我的老師Ian一樣成功")
                except sqlalchemy.exc.SQLAlchemyError as err:
                    db.rollback()
                    return self.jsonResponse(HTTPStatus.INTERNAL_SERVER_ERROR, str(err))
        else:
            return self.jsonResponse(HTTPStatus.UNAUTHORIZED, "請先登入")

    def phonebookHandler(self):
        if self.isLoggedIn():
            if self.command == 'GET':
                response_phonebook = []
                users = set()
                for i in range(len(videoMessage) - 1, -1, -1):
                    if (datetime.now() - videoMessage[i].create_time).total_seconds() < 300 and videoMessage[i].username not in users:
                        response_phonebook.append(videoMessage[i].to_json())
                        users.add(videoMessage[i].username)
                response_phonebook = list(reversed(response_phonebook))
                return self.jsonResponse(HTTPStatus.OK, response_phonebook)
            elif self.command == 'POST':
                try:
                    videoMessage.append(phonebook(self.body['username'], self.body['sdp'], self.body['candidates'], self.body['target']))
                    return self.jsonResponse(HTTPStatus.OK, None)
                except:
                    return self.jsonResponse(HTTPStatus.BAD_REQUEST, None)
            elif self.command == 'DELETE':
                try:
                    i = 0
                    while (True):
                        if (i == len(videoMessage)) :
                            break
                        if (self.body['username'] == videoMessage[i].username):
                            del videoMessage[i]
                        else:
                            i = i + 1
                    return self.jsonResponse(HTTPStatus.OK, None)
                except Exception as err:
                    return self.jsonResponse(HTTPStatus.BAD_REQUEST, str(err))
            else:
                return self.jsonResponse(HTTPStatus.BAD_REQUEST, "No support")
        else:
            return self.jsonResponse(HTTPStatus.UNAUTHORIZED, None)

    def fileHandler(self):
        path = self.translate_path(self.path)
        f = None
        if path.endswith("/"):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            fs = os.fstat(f.fileno())
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", self.guess_type(path))
            self.send_header("Content-Length", str(fs[6]))
            self.send_header(
                "Last-Modified", email.utils.formatdate(time.time(), usegmt=True))
            self.end_headers()
            return f.read()
        finally:
            f.close()

    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = self.directory
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

    def guess_type(self, path):
        guess = mimetypes.guess_type(path)[0]
        return guess if guess else 'application/octet-stream'
        # if guess:
        #     return guess
        # return 'application/octet-stream'
