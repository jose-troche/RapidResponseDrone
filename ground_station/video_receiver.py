#!/usr/bin/env python3

import cv2
import multiprocessing
import time
import sigint_handler
from database import VIDEO_FRAME, SHUTDOWN, db_initialize
from multiprocessing.managers import DictProxy

# Captures video frames from the drone and publishes them to the db
# so other processes can grab them.
def video_receiver(db: DictProxy):
    VIDEO_URL = 'udp://0.0.0.0:11111'
    is_frame_captured = False
    
    while not db.get(SHUTDOWN, False):
        if not is_frame_captured:
            print('Trying to acquire video feed ...')
            capture = cv2.VideoCapture(VIDEO_URL)
        else:
            db[VIDEO_FRAME] = frame

        is_frame_captured, frame = capture.read()


    print('Shutting down the Video Receiver')
    if capture:
        capture.release()
    cv2.destroyAllWindows()


# ---------------------------------------------------------------------
# The following is only an example of how to call the video_receiver 
# and how to get the video frames from the db

def image_processor_test(db: DictProxy):
    while not db.get(SHUTDOWN, False):
        frame = db[VIDEO_FRAME]
        print('Reading image frame with size', 0 if frame is None else len(frame))
        time.sleep(2)

    print('Shutting down the Image Processor')

if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db_initialize(db)

        processes = [
            multiprocessing.Process(target=target, args=(db, ))
            for target in [image_processor_test, video_receiver]
        ]

        for p in processes:
            p.start()

        while not sigint_handler.shutdown_signal:
            print('Main process running')
            time.sleep(1)

        print('Main process shutting down')

        db[SHUTDOWN] = True

        for p in processes:
            p.join()
