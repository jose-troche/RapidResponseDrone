from multiprocessing.managers import DictProxy

# Database keys
SHUTDOWN = 'SHUTDOWN'
VIDEO_FRAME = 'VIDEO_FRAME'
RECOGNIZED_OBJECTS = 'RECOGNIZED_OBJECTS'
SEARCHED_OBJECTS = 'SEARCHED_OBJECTS'
FIRE_LASER = 'FIRE_LASER'
VOICE_COMMAND = 'VOICE_COMMAND'
REPORT_GENERATED = 'REPORT_GENERATED'


def db_initialize(db: DictProxy):
    db[SHUTDOWN] = False
    db[VIDEO_FRAME] = None
    db[RECOGNIZED_OBJECTS] = []
    db[SEARCHED_OBJECTS] = set(['plant', 'f35'])
    db[FIRE_LASER] = False
    db[VOICE_COMMAND] = None
    db[REPORT_GENERATED] = None

