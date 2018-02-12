#!/usr/bin/env python3

import cv2

from eagleeyetracker import comm, detect, tracker

cap = cv2.VideoCapture(0)
location = (0, 0)

while True:
    frame = cap.read()
    location = detect.get_coords(frame, location)
    th, phi = tracker.img_coords_to_coords(*location)
    comm.send_coords(th, phi)

