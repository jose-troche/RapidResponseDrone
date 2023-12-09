#!/usr/bin/env python3

import cv2
import multiprocessing
import numpy
import signal
import time
from database_keys import VIDEO_FRAME, SHUTDOWN
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
            image_encoded = cv2.imencode('.jpg', frame)[1]
            image_bytes = (numpy.array(image_encoded)).tobytes()
            db[VIDEO_FRAME] = image_bytes

        is_frame_captured, frame = capture.read()


    print('Shutting down the Video Receiver')
    if capture:
        capture.release()
    cv2.destroyAllWindows()


# ---------------------------------------------------------------------
# The following is only an example of how to call the video_receiver 
# and how to get the video frames from the db
shutdown = False
def signal_handler(signum, frame):
    print(f'SIGINT received at "{frame.f_code.co_name}" with signal {signum}')
    global shutdown
    shutdown = True
signal.signal(signal.SIGINT, signal_handler)

def image_processor(db: DictProxy):

    while not db.get(SHUTDOWN, False):
        print('Reading image frame with size', len(db.get(VIDEO_FRAME, '')))
        time.sleep(2)

    print('Shutting down the Image Processor')

if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        db = manager.dict()

        processes = [
            multiprocessing.Process(target=target, args=(db, ))
            for target in [image_processor, video_receiver]
        ]

        for p in processes:
            p.start()

        while not shutdown:
            print('Main process running')
            time.sleep(1)

        print('Main process shutting down')

        db[SHUTDOWN] = True

        for p in processes:
            p.join()
