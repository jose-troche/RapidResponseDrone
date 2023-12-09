#!/usr/bin/env python3

import cv2
import multiprocessing
import numpy
from event_bus import EventBus
from database_keys import FRAME
from multiprocessing.managers import DictProxy

# Captures video frames from the drone and publishes them to the db
# so other processes can grab them.
# It also checks whether the shutdown event is set to terminate
def video_receiver(db: DictProxy, shutdown: multiprocessing.Event):
    VIDEO_URL = 'udp://0.0.0.0:11111'
    is_frame_captured = False
    
    while not shutdown.is_set():
        if not is_frame_captured:
            print("Trying to acquire video feed ...")
            capture = cv2.VideoCapture(VIDEO_URL)
        else:
            image_encoded = cv2.imencode('.jpg', frame)[1]
            image_bytes = (numpy.array(image_encoded)).tobytes()
            db[FRAME] = image_bytes

        is_frame_captured, frame = capture.read()


    print("Shutting down the Video Receiver")
    if capture:
        capture.release()
    cv2.destroyAllWindows()


# ---------------------------------------------------------------------
# The following is only an example of how to call the video_receiver 
# and how to get the video frames from the event_bus
def on_video_frame_received(frame):
        print(f'Frame Size: {len(frame)}')

if __name__ == '__main__':
    # event_bus = EventBus()
    # event_bus.add_listener(EventBus.VIDEO_FRAME, on_video_frame_received)

    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db[FRAME] = ''

        shutdown = multiprocessing.Event()

        p = multiprocessing.Process(target=video_receiver, args=(db, shutdown))

        p.start()

        # Ctrl+C to stop main
        try:
            while True:
                print(f'Frame Size: {len(db[FRAME])}')
        finally:
            print("Shutting down")
            shutdown.set()
            p.join()


    
