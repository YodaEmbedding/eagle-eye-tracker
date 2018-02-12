import numpy as np
import cv2

cap = cv2.VideoCapture(2)

# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 4,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Create some random colors
color = np.random.randint(0,255,(100,3))

old_gray = None

while True:
    ret,frame = cap.read()
    
    # flip
    # frame = frame[:, ::-1, :]
    frame = cv2.flip(frame, 1)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    if old_gray is None:
        # Create a mask image for drawing purposes
        mask = np.zeros_like(frame)
        # Take first frame and find corners in it
        p0 = cv2.goodFeaturesToTrack(frame_gray, mask = None, **feature_params)
        old_gray = frame_gray
        continue

    if p0.shape[0] < 4:
        new_pts = cv2.goodFeaturesToTrack(frame_gray, mask = None, **feature_params)
        p0 = np.concatenate((p0, new_pts[:4 - p0.shape[0]]))

    # calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    if p1 is None:
        p1 = np.zeros((0,0), np.float32)
        st = np.zeros(0, np.float32)
    else:
        p1 = np.squeeze(p1, axis=1)
        st = np.squeeze(st)
    
    # Select good points
    good_new = p1[st==1]
    good_old = p0[st==1]

    # draw the tracks
    mask = (0.8 * mask).astype(dtype=np.uint8)
    for i,(new,old) in enumerate(zip(good_new,good_old)):
        a,b = new.ravel()
        c,d = old.ravel()
        mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
        frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)
    img = cv2.add(frame,mask)

    cv2.imshow('frame',img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

    # Now update the previous frame and previous points
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1,1,2)

cv2.destroyAllWindows()
cap.release()
