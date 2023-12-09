#!/usr/bin/env python3

import multiprocessing
from video_receiver import video_receiver
from webserver import webserver
from database_keys import FRAME

if __name__ == '__main__':
    # event_bus = EventBus()
    # event_bus.add_listener(EventBus.VIDEO_FRAME, on_video_frame_received)

    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db[FRAME] = b''

        shutdown = multiprocessing.Event()

        processes = [
            multiprocessing.Process(target=target, args=(db, shutdown))
            for target in [webserver, video_receiver]
        ]

        for p in processes:
            p.start()

        # Ctrl+C to stop main
        try:
            while True:
                pass
        finally:
            print("Shutting down ALL processes")
            shutdown.set()
            for p in processes:
                p.join()