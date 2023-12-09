#!/usr/bin/env python3

from http.server import SimpleHTTPRequestHandler, HTTPServer
from http import HTTPStatus
from multiprocessing.managers import DictProxy
from urllib.parse import urlparse, parse_qs
from database_keys import VIDEO_FRAME, SHUTDOWN
from selectors import DefaultSelector, EVENT_READ
import threading
import socket
import time
import multiprocessing
import sigint_handler

TELLO_IP = "192.168.10.1"
TELLO_COMMAND_PORT = 8889
TELLO_COMMAND_ADDRESS = (TELLO_IP, TELLO_COMMAND_PORT)

UDP_SOCKET = socket.socket(socket.AF_INET,    # Internet
                           socket.SOCK_DGRAM) # UDP




# Send a command to the drone via the UDP socket
def send_to_tello(command: str):
    UDP_SOCKET.sendto(command.encode(), TELLO_COMMAND_ADDRESS)


# Send periodically a drone command to keep connection alive
def keep_alive():
    while True:
        print("Sending keep alive")
        send_to_tello("command")
        time.sleep(10)


is_keep_alive_running = False

# The HTTP handler
class Handler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='webassets', **kwargs)


    def do_GET(self) -> None:
        global is_keep_alive_running
        path = self.path

        if path == "/":
            self.send_response(HTTPStatus.MOVED_PERMANENTLY)
            self.send_header("Location", "/drone_pilot.html")
            self.end_headers()

        elif path.endswith((".html", ".htm", ".js", ".css")):
            super().do_GET()

        elif path.startswith("/drone"):
            params = parse_qs(urlparse(path).query, max_num_fields=1)
            command = params['command'][0] if 'command' in params else ""
            self.send_response(HTTPStatus.OK)
            self.end_headers()

            if command: # Send command to tello drone if not empty
                if command == "takeoff" and not is_keep_alive_running:
                    is_keep_alive_running = True
                    print("Starting keep alive daemon")
                    threading.Thread(
                        target=keep_alive, daemon=True).start()
                    

                send_to_tello(command)

        elif path.startswith("/video_frame"):
            image_bytes = self.server.db.get(VIDEO_FRAME, b'')
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "image/jpeg")
            self.send_header("Content-length", str(len(image_bytes)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(image_bytes)

        elif path.startswith("/events"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "text/event-stream")
            self.end_headers()

            # Send a message to the client.
            self.wfile.write(b"data: Hello, world!\n\n")

            # Keep the connection open.
            while True:
                time.sleep(1)
                self.wfile.write((f"data: {time.time()} This is a message from the server.\n\n").encode())


        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Resource not found")


    def log_message(self, format, *args):
        # Filter out repetitive logs
        if (not self.path.startswith('/video_frame') and 
            not self.path == '/drone?command=rc%200.0000%200.0000%200.0000%200.0000'):
            super().log_message(format, *args)


class DroneHTTPServer(HTTPServer):
    def __init__(self,
                 server_address,
                 RequestHandlerClass,
                 db: DictProxy,
                 bind_and_activate: bool = True) -> None:

        self.db = db # Add a reference to the db
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)


def webserver(db: DictProxy):
    HTTP_SERVER_PORT = 8000
    with DroneHTTPServer(('', HTTP_SERVER_PORT), Handler, db) as httpd:
        print(f'Drone HTTP server listening at port {HTTP_SERVER_PORT}')

        # From https://docs.python.org/3/library/signal.html
        selector = DefaultSelector()
        selector.register(httpd, EVENT_READ)

        while not db.get(SHUTDOWN, False):
            for key, _ in selector.select():
                if key.fileobj == httpd:
                    httpd.handle_request()

        print(f'Shutting down the Webserver')


# ---------------------------------------------------------------------
# The following is only an example of how to start the webserver

if __name__ == '__main__':

    with multiprocessing.Manager() as manager:
        db = manager.dict()

        p = multiprocessing.Process(target=webserver, args=(db, ))
        p.start()

        while not sigint_handler.shutdown_signal:
            time.sleep(1)

        print('Main process shutting down ...')

        # Signal all subprocesses to shutdown
        db[SHUTDOWN] = True
        
        # Wait for them to finish
        p.join()

        print('Shutdown complete')
