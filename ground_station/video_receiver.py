#!/usr/bin/env python3

import cv2
import multiprocessing
from event_bus import EventBus

# Captures video frames from the drone and publishes them to the event_bus
# so other processes can grab them.
# It also checks whether the shutdown event to terminate
def video_receiver(event_bus: EventBus, shutdown: multiprocessing.Event):
    VIDEO_URL = 'udp://0.0.0.0:11111'
    is_frame_captured = False
    
    while not shutdown.is_set():
        if not is_frame_captured:
            print("Trying to acquire video feed ...")
            capture = cv2.VideoCapture(VIDEO_URL)
        else:
            event_bus.emit(EventBus.VIDEO_FRAME, frame)

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
    event_bus = EventBus()
    event_bus.add_listener(EventBus.VIDEO_FRAME, on_video_frame_received)

    shutdown = multiprocessing.Event()

    p = multiprocessing.Process(target=video_receiver, args=(event_bus, shutdown))

    p.start()

    # Ctrl+C to stop main
    try:
        while True:
            pass
    finally:
        shutdown.set()


    
