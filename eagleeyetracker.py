#!/usr/bin/env python3

import cv2
import numpy as np

from eagleeyetracker import comm, detect, tracker

cap = cv2.VideoCapture(2)
location = (0, 0)

detector = detect.Detector()
color = np.random.randint(0, 255, (100, 3))

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    detector.next(frame)
    comm.send(*detector.location)

    # Create a mask image for drawing purposes
    mask = np.zeros_like(detector.frame)

    # draw the tracks
    mask = (0.8 * mask).astype(dtype=np.uint8)
    for i, (new, old) in enumerate(zip(detector.good_new, detector.good_old)):
        a,b = new.ravel()
        c,d = old.ravel()
        mask = cv2.line(mask, (a, b), (c,d), color[i].tolist(), 2)
        frame = cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
    img = cv2.add(frame,mask)

    # keypresses
    cv2.imshow('frame', img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()
