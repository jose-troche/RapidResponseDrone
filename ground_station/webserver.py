#!/usr/bin/env python3

from http.server import SimpleHTTPRequestHandler, HTTPServer
from http import HTTPStatus
from multiprocessing.managers import DictProxy
from typing import Any
from urllib.parse import urlparse, parse_qs
from database_keys import FRAME
import threading
import socket
import time
import multiprocessing

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

    def log_message(self, format, *args):
        if (not self.path.startswith('/video_frame') and 
            not self.path == '/drone?command=rc%200.0000%200.0000%200.0000%200.0000'):
            super().log_message(format, *args)

    def do_GET(self) -> None:
        global is_keep_alive_running
        path = self.path

        if path == "/":
            self.send_response(HTTPStatus.MOVED_PERMANENTLY)
            self.send_header("Location", "/drone_pilot.html")
            self.end_headers()
        elif path.endswith((".html", ".htm", ".js", ".jpg")):
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
            image_bytes = self.server.db[FRAME]
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


class DroneHTTPServer(HTTPServer):
    def __init__(self,
                 server_address,
                 RequestHandlerClass,
                 db: DictProxy,
                 bind_and_activate: bool = True) -> None:

        self.db = db
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)


def webserver(db: DictProxy, shutdown: multiprocessing.Event):
    HTTP_SERVER_PORT = 8000
    with DroneHTTPServer(('', HTTP_SERVER_PORT), Handler, db) as httpd:
        print(f'Drone HTTP server listening at port {HTTP_SERVER_PORT}')
        #multiprocessing.Process(target=shutdown_webserver, args=(httpd, shutdown)).start()
        httpd.serve_forever()


def shutdown_webserver(httpd: HTTPServer, shutdown: multiprocessing.Event):
    while not shutdown.is_set():
        pass

    print("Shuting down the webserver")
    httpd.shutdown()


# ---------------------------------------------------------------------
# The following is only an example of how to start the webserver


if __name__ == '__main__':
    # event_bus = EventBus()
    # event_bus.add_listener(EventBus.VIDEO_FRAME, on_video_frame_received)

    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db[FRAME] = b''

        shutdown = multiprocessing.Event()

        p = multiprocessing.Process(target=webserver, args=(db, shutdown))

        p.start()

        # Ctrl+C to stop main
        try:
            while True:
                pass
        finally:
            print("Shutting down")
            shutdown.set()
            p.join()