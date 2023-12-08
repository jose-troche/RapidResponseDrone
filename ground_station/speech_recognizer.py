#!/usr/bin/env python3

import multiprocessing
import time
from event_bus import EventBus

# Captures spoken sound and converts speech to text commands
# It also checks whether the shutdown event is set to terminate
def speech_recognizer(event_bus: EventBus, shutdown: multiprocessing.Event):
    
    while not shutdown.is_set():
        print('Converting speech to text ...')
        # Examples of commands: takeoff, land, target tv
        voice_command = f'target computer {time.time()}'
        event_bus.emit(EventBus.VOICE_COMMAND, voice_command)
        time.sleep(5)

    print("Shutting down the Speech Recognizer")
    # Clean up 


# ---------------------------------------------------------------------
# The following is only an example of how to call the speech_recognizer 
# and how to get the text command from the event_bus
def on_voice_command(voice_command):
        print(f'Voice command: {voice_command}')

if __name__ == '__main__':
    event_bus = EventBus()
    event_bus.add_listener(EventBus.VOICE_COMMAND, on_voice_command)

    shutdown = multiprocessing.Event()

    p = multiprocessing.Process(target=speech_recognizer, args=(event_bus, shutdown))

    p.start()

    # Ctrl+C to stop main
    try:
        while True:
            pass
    finally:
        shutdown.set()
