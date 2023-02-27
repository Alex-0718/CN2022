import socket
import threading
import selectors
import sys

# Windows: SelectSelector, Linux: PollSelector
Selector = selectors.PollSelector if hasattr(selectors, 'PollSelector') else selectors.SelectSelector

class ThreadingHTTPServer:
    timeout = None
    queue_size = 5

    def __init__(self, server_address, RequestHandlerClass):
        self.RequestHandlerClass = RequestHandlerClass
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(server_address)
            print("Listening:", self.socket.getsockname())
            self.socket.listen(self.queue_size)
        except:
            self.socket.close()
            # self.server_close()
            raise

    def serve(self, interval=0.5):
        with Selector() as selector:
            selector.register(self, selectors.EVENT_READ)

            while True:
                ready = selector.select(interval)
                if ready:
                    self.handle_request()

    def handle_request(self):
        try:
            request, client_address = self.socket.accept()
        except OSError:
            return
            
        try:
            self.process_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
            self.shutdown_request(request)
        except:
            self.shutdown_request(request)
            raise

    def process_request(self, request, client_address):
        t = threading.Thread(target = self.process_request_threading,
                             args = (request, client_address), daemon = True)
        t.start()

    def process_request_threading(self, request, client_address):
        try:
            self.RequestHandlerClass(request, client_address, self)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)
    
    def handle_error(self, request, client_address):
        print('Exception occurred during processing of request from', client_address, file=sys.stderr)
        import traceback
        traceback.print_exc()

    def shutdown_request(self, request):
        try:
            request.shutdown(socket.SHUT_WR)
        except OSError:
            pass 
        request.close()
        # self.disconnect(request)

    # def server_close(self):
    #     self.socket.close()

    # def disconnect(self, request):
    #     request.close()
        
    def fileno(self):
        return self.socket.fileno()

    # def __enter__(self):
    #     return self

    # def __exit__(self, *args):
        # self.server_close()