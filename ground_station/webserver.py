#!/usr/bin/env python3

from http.server import SimpleHTTPRequestHandler, HTTPServer
from http import HTTPStatus
from multiprocessing.managers import DictProxy
from urllib.parse import urlparse, parse_qs
from database import VIDEO_FRAME, SHUTDOWN, RECOGNIZED_OBJECTS, db_initialize
from selectors import DefaultSelector, EVENT_READ
from drone_commander import send_command_to_drone
import time
import json
import multiprocessing
import sigint_handler
import video_frame


# The HTTP handler
class Handler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='webassets', **kwargs)


    def do_GET(self) -> None:
        global is_keep_alive_running
        path = self.path

        if path == '/':
            self.send_response(HTTPStatus.MOVED_PERMANENTLY)
            self.send_header('Location', '/drone_pilot.html')
            self.end_headers()

        elif path.endswith(('.html', '.htm', '.js', '.css')):
            super().do_GET()

        elif path.startswith('/drone'):
            params = parse_qs(urlparse(path).query, max_num_fields=1)
            command = params['command'][0] if 'command' in params else ''
            self.send_response(HTTPStatus.OK)
            self.end_headers()

            if command: # Send command to tello drone if not empty
                send_command_to_drone(command)

        elif path.startswith('/video_frame'):
            frame = self.server.db.get(VIDEO_FRAME)
            image = b'' if frame is None else video_frame.to_jpg(video_frame.resize(frame, 0.8))

            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'image/jpeg')
            self.send_header('Content-length', str(len(image)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(image)

        elif path.startswith('/recognized_objects'):
            recognized_objects = json.dumps(self.server.db[RECOGNIZED_OBJECTS]).encode()
            self.server.db[RECOGNIZED_OBJECTS] = [] # Clear the recognized objects

            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            #self.send_header('Content-length', str(len(recognized_objects)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(recognized_objects)

        else:
            self.send_error(HTTPStatus.NOT_FOUND, 'Resource not found')


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
        db_initialize(db)

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
