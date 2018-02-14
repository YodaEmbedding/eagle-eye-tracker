import cv2
import numpy as np

# TODO rename variables, e.g. good_new
class Detector(object):
    def __init__(self):
        # params for ShiTomasi corner detection
        self.feature_params = dict(
            maxCorners=4,
            qualityLevel=0.3,
            minDistance=7,
            blockSize=7)

        # Parameters for lucas kanade optical flow
        self.lk_params = dict(
            winSize=(15,15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        self.location = np.zeros((1, 1), np.uint8)  # TODO uint8
        self.good_old = np.zeros((0, 0), np.float32)
        self.good_new = np.zeros((0, 0), np.float32)
        self.old_gray = None

    def next(self, frame):
        self.frame = frame
        self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        if self.old_gray is None:
            # Take first frame and find corners in it
            self.p0 = cv2.goodFeaturesToTrack(self.frame_gray, mask = None,
                **self.feature_params)
            self.old_gray = self.frame_gray
            return

        if self.p0.shape[0] < 4:
            new_pts = cv2.goodFeaturesToTrack(self.frame_gray, mask = None,
                **self.feature_params)
            self.p0 = np.concatenate((self.p0, new_pts[:4 - self.p0.shape[0]]))

        # calculate optical flow
        self.p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray,
            self.frame_gray, self.p0, None, **self.lk_params)

        if self.p1 is None:
            self.p1 = np.zeros((0, 0), np.float32)
            st = np.zeros(0, np.float32)
        else:
            self.p1 = np.squeeze(self.p1, axis=1)
            st = np.squeeze(st)

        # Select good points
        self.good_new = self.p1[st==1]
        self.good_old = self.p0[st==1]

        # Now update the previous frame and previous points
        self.old_gray = self.frame_gray.copy()  #TODO rm
        self.p0 = self.good_new.reshape(-1,1,2)

        self.location = (self.p0[0] if self.p0.shape[0] > 0
            else np.zeros((1, 1), np.float32)) # TODO type

