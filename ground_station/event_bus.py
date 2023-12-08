# Original source: https://www.joeltok.com/posts/2021-03-building-an-event-bus-in-python/

from multiprocessing import Process
from collections.abc import Callable

# An event bus class
# listeners (subscribers) can register (subscribe) an async function to listen to specific events
# When an event is emitted (published) all listener functions are called with event_data
class EventBus():

    # Event names
    VIDEO_FRAME = 'VIDEO_FRAME'
    IMAGE_RECOGNITION_RESULT = 'IMAGE_RECOGNITION_RESULT'
    TARGET_DETECTED = 'TARGET_DETECTED'
    VOICE_COMMAND = 'VOICE_COMMAND'

    # Event set
    EVENTS = set([
        VIDEO_FRAME,
        IMAGE_RECOGNITION_RESULT,
        TARGET_DETECTED,
        VOICE_COMMAND
    ])

    def __init__(self):
        # Dictionary with event_names as keys and set of listeners as values
        self.event_listeners = {}

    # Add a listener to an event_name set
    def add_listener(self, event_name: str, listener: Callable):
        if not event_name in self.EVENTS:
            raise Exception(f"Event {event_name}  not supported")

        if not callable(listener):
             raise Exception(f"The listener must be a callable function")

        if not self.event_listeners.get(event_name, None):
            self.event_listeners[event_name] = set([listener])
        else:
            self.event_listeners[event_name].add(listener)

    # Remove a specific listener from an event_name set
    def remove_listener(self, event_name: str, listener: Callable):
        if event_name not in self.event_listeners:
            return

        if listener in self.event_listeners[event_name]:
            self.event_listeners[event_name].remove(listener)

        if len(self.event_listeners[event_name]) == 0:
            del self.event_listeners[event_name]

    # Emit the event_name by calling all registered listeners with event_data as argument
    def emit(self, event_name: str, event_data=None):
        listeners = self.event_listeners.get(event_name, [])
        for listener in listeners:
            Process(target=listener, args=(event_data,)).start()
