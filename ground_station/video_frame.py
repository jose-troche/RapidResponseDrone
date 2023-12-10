import cv2
import numpy
from cv2.typing import MatLike


# Crops a frame by a margin in all 4 sides (the center piece of the frame is returned)
def crop_margin(frame: MatLike, margin: int):
    return frame[margin:-margin, margin:-margin]


# Resizes frame using a ratio. e.g. 0.5 is half the size, 0.75 is 75%
def resize(frame: MatLike, ratio: float):
    return cv2.resize(frame, (0,0), fx=ratio, fy=ratio)


# Converts a frame to a JPEG image. Its bytes are retuned
def to_jpg(frame: MatLike):
    jpeg_encoded = cv2.imencode('.jpg', frame)[1]
    return (numpy.array(jpeg_encoded)).tobytes()