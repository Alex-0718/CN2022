# from http.server import SimpleHTTPRequestHandler
# from HTTPrequests import SimpleHTTPRequestHandler 
from HTTPAPIHandler import HTTPAPIHandler 
from HTTPthreading_refactor import ThreadingHTTPServer
import ssl

httpd = ThreadingHTTPServer(('', 14443), HTTPAPIHandler)
sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
sslctx.check_hostname = False # If set to True, only the hostname that matches the certificate will be accepted
sslctx.load_cert_chain(certfile='./ssh/cert.pem', keyfile="./ssh/key.pem")
httpd.socket = sslctx.wrap_socket(httpd.socket, server_side=True)
httpd.serve()
