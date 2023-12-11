#!/usr/bin/env python3

import multiprocessing
import time
import sigint_handler
import threading
import boto3
import video_frame
from queue import Queue
from video_receiver import video_receiver
from laser_commander import laser_commander
from database import VIDEO_FRAME, SHUTDOWN, RECOGNIZED_OBJECTS, SEARCHED_OBJECTS, db_initialize
from multiprocessing.managers import DictProxy

# Gets the current video frame and sends it to rekognition for object/label detection
# Updates the db with the objects recognized/detected
def object_recognizer(db: DictProxy):
    rekognition = boto3.client('rekognition', region_name='us-east-2')

    # Start laser_commander
    laser_queue = Queue()
    threading.Thread(target=laser_commander, args=(laser_queue,)).start()
  
    while not db[SHUTDOWN]:
        frame = db[VIDEO_FRAME]
        if not frame is None:
            cropped_frame = video_frame.crop_margin(frame, 100)
            image_bytes = video_frame.to_jpg(cropped_frame)
            try:
                response = rekognition.detect_labels(
                    Image={'Bytes': image_bytes},
                    MinConfidence=77.5
                )
                recognized_objects = [ label['Name'].lower().strip() for label in response['Labels'] ]
                db[RECOGNIZED_OBJECTS] = recognized_objects
            except:
                print('Error when calling AWS Rekognition')

            if recognized_objects in db[SEARCHED_OBJECTS]:
                # Turn on laser
                laser_queue.put_nowait(1)

        time.sleep(0.75)

    print('Shutting down the Object Recognizer')


# ---------------------------------------------------------------------
# The following is only an example of how to start the object_recognizer 

def recognized_objects_processor_test(db: DictProxy):
    while not db.get(SHUTDOWN, False):
        recognized_objects = db[RECOGNIZED_OBJECTS]
        if recognized_objects:
            print('Recognized objects', ','.join(recognized_objects))
        db[RECOGNIZED_OBJECTS] = []
        time.sleep(2)

    print('Shutting down the recognized_objects_processor_test')

if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db_initialize(db)

        processes = [
            multiprocessing.Process(target=target, args=(db, ))
            for target in [object_recognizer, video_receiver, recognized_objects_processor_test]
        ]

        for p in processes:
            p.start()

        while not sigint_handler.shutdown_signal:
            print('Main process running')
            time.sleep(3)

        print('Main process shutting down')

        db[SHUTDOWN] = True

        for p in processes:
            p.join()
