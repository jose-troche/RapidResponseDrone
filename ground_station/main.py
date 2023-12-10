#!/usr/bin/env python3

import multiprocessing
import sigint_handler
import time
from video_receiver import video_receiver
from object_recognizer import object_recognizer
from webserver import webserver
from database import SHUTDOWN, db_initialize

if __name__ == '__main__':

    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db_initialize(db)

        processes = [
            multiprocessing.Process(target=target, args=(db, ))
            for target in [webserver, video_receiver, object_recognizer]
        ]

        for p in processes:
            p.start()

        while not sigint_handler.shutdown_signal:
            time.sleep(1)

        print('Main process shutting down ...')

        # Signal all processes to shutdown
        db[SHUTDOWN] = True

        # Wait for them to finish
        for p in processes:
            p.join()

        print('Shutdown complete')
