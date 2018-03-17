#!/usr/bin/env python3

import cv2
import numpy as np

from eagleeyetracker.comm import Communicator
from eagleeyetracker.detect import Detector

ENABLE_COMM = True

cap = cv2.VideoCapture(2)

detector = Detector()
if ENABLE_COMM: communicator = Communicator()
color = np.random.randint(0, 255, (100, 3))
mask = None

while True:
    ret, frame = cap.read()
    # frame = cv2.flip(frame, 1)

    detector.next(frame)
    raw_coords = np.flip(frame.shape[0:2], axis=0)
    scale = 2. / np.max(raw_coords)
    offset = 0.5 * np.array(raw_coords)
    coords = tuple(scale * (detector.location - offset))

    if ENABLE_COMM: communicator.send_coords(*coords)

    # Create a mask image for drawing purposes
    if mask is None:
        mask = np.zeros_like(frame)

    # Draw the tracks
    mask = (0.8 * mask).astype(dtype=np.uint8)
    frame = cv2.circle(frame, tuple(detector.location), 10, (0, 0, 255), -1)
    for i, (new, old) in enumerate(zip(detector.good_new, detector.good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        mask = cv2.line(mask, (a, b), (c,d), color[i].tolist(), 2)
        frame = cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
    img = cv2.add(frame, mask)

    cv2.imshow('Preview', img)

    key = cv2.waitKey(30) & 0xff
    if key == 27:
        break

cv2.destroyAllWindows()
cap.release()
