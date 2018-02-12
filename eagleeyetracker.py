import cv2

def get_coords(frame, location):
    """Gets coordinates of object from input frame

    Assumptions:
        Specify starting point (i.e. center point)
        Track it with optical flow
    """

    raise NotImplementedError
    # return cv2.optical_flow(frame, prev_frame, location)

def img_coords_to_coords(dx, dy):
    """Converts image coordinates to real-world coordinates"""
    dphi, dth = dx, dy
    return dphi, dth

def send_coords(th, phi):
    """Sends coordinates to microcontroller"""
    raise NotImplementedError
    # send_bt('th=' + th)
    # send_bt('phi=' + phi)

cap = cv2.VideoCapture(0)
location = (0, 0)

while True:
    frame = cap.read()
    location = get_coords(frame, location)
    th, phi = img_coords_to_coords(*location)
    send_coords(th, phi)

