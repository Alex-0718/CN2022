import sys
import html
import time
import enum
import socket
import email.parser
import email.message
import json

DEFAULT_ERROR_MESSAGE = """\
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: %(code)d</p>
        <p>Message: %(message)s.</p>
        <p>Error code explanation: %(code)s - %(explain)s.</p>
    </body>
</html>
"""
DEFAULT_ERROR_CONTENT_TYPE = "text/html;charset=utf-8"
_MAXLINE, _MAXHEADERS = 65536, 100


class HTTPStatus(enum.IntEnum):
    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.phrase = phrase
        obj.description = description
        return obj

    OK = 200, 'OK', 'Request fulfilled, document follows'
    BAD_REQUEST = 400, 'Bad Request', 'Bad request syntax or unsupported method'
    UNAUTHORIZED = 401, 'Unauthorized', 'No permission -- see authorization schemes'
    NOT_FOUND = 404, 'Not Found', 'Nothing matches the given URI'
    LENGTH_REQUIRED = (411, 'Length Required', 'Client must specify Content-Length')
    REQUEST_URI_TOO_LONG = 414, 'Request-URI Too Long', 'URI is too long'
    UNSUPPORTED_MEDIA_TYPE = (415, 'Unsupported Media Type', 'Entity body in unsupported format')
    REQUEST_HEADER_FIELDS_TOO_LARGE = (431, 'Request Header Fields Too Large',
                                       'The server is unwilling to process the request because its header '
                                       'fields are too large')
    INTERNAL_SERVER_ERROR = (500, 'Internal Server Error', 'Server got itself in trouble')
    NOT_IMPLEMENTED = 501, 'Not Implemented', 'Server does not support this operation'
    HTTP_VERSION_NOT_SUPPORTED = 505, 'HTTP Version Not Supported', 'Cannot fulfill request'

class HTTPrequestHandler():
    error_message_format = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE

    protocol_version = "HTTP/1.1"
    responses = {
        v: (v.phrase, v.description)
        for v in HTTPStatus.__members__.values()
    }

    def __init__(self, request, client_address, server):
        self.connection = self.request = request
        self.client_address = client_address

        self.rfile = self.connection.makefile('rb')
        self.wfile = self.connection.makefile('wb')
        try:
            self.close_connection = True
            self.handle_request()
            while not self.close_connection:
                self.handle_request()
        finally:
            if not self.wfile.closed:
                try:
                    self.wfile.flush()
                except socket.error:
                    pass
            self.wfile.close()
            self.rfile.close()

    # handle_request 處理請求(會呼叫parse_request)
    def handle_request(self):  # 讀取
        self.raw_requestline = self.rfile.readline(_MAXLINE + 1)
        if len(self.raw_requestline) > _MAXLINE:
            self.requestline = self.request_version = self.command = ''
            self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
            return
        if not self.raw_requestline:
            self.close_connection = True
            return
        if not self.parse_request():
            return
        self.routeHandler()
        self.wfile.flush()

    # parse_request 解析使用者的請求看合不合理
    def parse_request(self):
        self.command = self.close_connection = True
        self.requestline = str(self.raw_requestline, 'iso-8859-1').rstrip('\r\n')

        words = self.requestline.split(' ')
        if len(words) == 0:
            return False
        else:
            try:
                version = words[-1]
                if not version.startswith('HTTP/') or len(words) != 3:
                    raise ValueError
                base_version_number = version.split('/', 1)[1]
                version_number = float(base_version_number)
                if version_number >= 1.1 and self.protocol_version >= "HTTP/1.1":
                    self.close_connection = False
                if not 1.0 <= version_number < 2.0:
                    self.send_error(HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                        "Invalid HTTP version (%s)" % base_version_number)  
                    return False
                self.request_version = version
            except (ValueError):
                self.send_error(HTTPStatus.BAD_REQUEST,
                    "Bad request syntax (%r)" % self.requestline)
                return False

        self.command, self.path = words[:2]

        if self.path.startswith('//'):
            self.path = '/' + self.path.lstrip('/')

        # 讀取 headers
        try:
            self.headers = []
            while True:
                line = self.rfile.readline(_MAXLINE + 1)
                if len(line) > _MAXLINE:
                    self.send_error(
                        HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,  "Line too long")
                    return False
                self.headers.append(line)
                if len(self.headers) > _MAXHEADERS:
                    self.send_error(
                        HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                        "got more than %d headers" % _MAXHEADERS)
                    return False
                if line in (b'\r\n', b'\n', b''):
                    break
            hstring = b''.join(self.headers).decode('iso-8859-1')
            self.headers = email.parser.Parser(
                _class=email.message.Message).parsestr(hstring)

        except Exception as err:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                "Bad request header format",
                str(err))
            return False

        conntype = self.headers.get('Connection', "")
        if conntype.lower() == 'close':
            self.close_connection = True
        elif (conntype.lower() == 'keep-alive'):
            self.close_connection = False

        contentType = self.headers.get('Content-Type', "").strip()
        if contentType != '':
            if contentType.startswith('application/json'):
                try:
                    contentLength = int(self.headers.get('content-length', ''))
                except ValueError:
                    self.send_error(HTTPStatus.LENGTH_REQUIRED)
                    return False
                self.body = json.loads(self.rfile.read(contentLength))
            else:
                self.send_error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
                return False

        return True

    # send_error 遇到錯誤的時候會送出錯誤訊息
    def send_error(self, code, message=None, explain=None):
        shortmsg, longmsg = self.responses[code]
        if message is None:
            message = shortmsg
        if explain is None:
            explain = longmsg
        self.send_response(code, message)
        self.send_header('Connection', 'close')

        body = None
        if (code >= 200):
            content = (self.error_message_format % {
                'code': code,
                'message': html.escape(message, quote=False),
                'explain': html.escape(explain, quote=False)
            })
            body = content.encode('UTF-8')
            self.send_header("Content-Type", self.error_content_type)
            self.send_header('Content-Length', str(len(body)))
        self.end_headers()

        if self.command != 'HEAD' and body:
            self.wfile.write(body)

    # send_response 遇到正確的請求會送出應有的結果
    def send_response(self, code, message=None):
        code = code.value
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        
        self._headers_buffer.append(("%s %d %s\r\n" % (self.protocol_version, code, message)).encode('iso-8859-1'))
        self.send_header('Server', "HTTP/1.1 Poor Python")
        self.send_header('Date', email.utils.formatdate(None, usegmt=True))
        print(self.client_address[0], time.strftime("%Y-%m-%d, %H:%M:%S"), self.requestline, str(code), '-', file=sys.stderr)

    def send_header(self, keywords, value):
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        self._headers_buffer.append(("%s: %s\r\n" % (keywords, value)).encode('iso-8859-1'))

        if keywords.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = True
            elif value.lower() == 'keep-alive':
                self.close_connection = False

    def end_headers(self):
        self._headers_buffer.append(b"\r\n")
        if hasattr(self, '_headers_buffer'):
            self.wfile.write(b"".join(self._headers_buffer))
            self._headers_buffer = []
