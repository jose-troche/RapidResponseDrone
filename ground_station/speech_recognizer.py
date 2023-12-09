#!/usr/bin/env python3


import time
import multiprocessing
import sigint_handler
from database import SHUTDOWN, VOICE_COMMAND_QUEUE, db_initialize
from multiprocessing.managers import DictProxy


# Captures spoken sound and converts speech to text commands
# It also checks whether the shutdown event is set to terminate
def speech_recognizer(db: DictProxy):

    while not db.get(SHUTDOWN, False):
        print('Converting speech to text ...')
        # Examples of commands: takeoff, land, target tv
        voice_command = f'target computer {time.time()}'
        db[VOICE_COMMAND_QUEUE] = voice_command
        time.sleep(3)

    print("Shutting down the Speech Recognizer")
    # Clean up


# ---------------------------------------------------------------------
# The following is only an example of how to call the speech_recognizer
# and how to get the text command from the db
# You can start this with:
#     python speech_recognizer.py
# And Ctrl+C to shut it down

if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db_initialize(db)

        p = multiprocessing.Process(target=speech_recognizer, args=(db, ))

        p.start()

        while not sigint_handler.shutdown_signal:
            voice_command = db[VOICE_COMMAND_QUEUE]
            if voice_command:
                print(f'Got voice command: {voice_command}')
                db[VOICE_COMMAND_QUEUE] = None
            else:
                print('No voice command')
            time.sleep(1)

        print('Main process shutting down ...')

        # Signal all subprocesses to shutdown
        db[SHUTDOWN] = True

        # Wait for them to finish
        p.join()

        print('Shutdown complete')
