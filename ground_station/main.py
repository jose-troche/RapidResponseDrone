#!/usr/bin/env python3

import multiprocessing
import sigint_handler
import time
from video_receiver import video_receiver
from webserver import webserver
from database_keys import SHUTDOWN

if __name__ == '__main__':

    with multiprocessing.Manager() as manager:
        db = manager.dict()

        processes = [
            multiprocessing.Process(target=target, args=(db, ))
            for target in [webserver, video_receiver]
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
