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

        self.location = np.array([-1, -1], np.float32)
        self.good_old = np.zeros((0, 2), np.float32)
        self.good_new = np.zeros((0, 2), np.float32)
        self.old_gray = None

    def next(self, frame):
        self.frame = frame
        self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        if self.old_gray is None:
            # Take first frame and find corners in it
            self.p0 = cv2.goodFeaturesToTrack(self.frame_gray, mask = None,
                **self.feature_params)
            # TODO this is a strange way of doing things
            self.p0 = (np.array([], np.float32).reshape(0, 1, 2)
                if self.p0 is None else self.p0)
            self.old_gray = self.frame_gray
            return

        if self.p0.shape[0] < 4:
            new_pts = cv2.goodFeaturesToTrack(self.frame_gray, mask = None,
                **self.feature_params)
            # TODO eww...
            new_pts = (np.array([], np.float32).reshape(0, 1, 2)
                if new_pts is None else new_pts)
            self.p0 = np.vstack([self.p0, new_pts[:4 - self.p0.shape[0]]])

        # TODO think about what happens when no points at all to track
        if self.p0.shape[0] == 0:
            self.location = np.array([-1, -1], np.float32)
            return

        # calculate optical flow
        self.p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray,
            self.frame_gray, self.p0, None, **self.lk_params)

        # Normalize p1 and st
        if self.p1 is None:
            self.p1 = np.zeros((0, 0), np.float32)
            st = np.zeros(0, np.float32)
        else:
            self.p1 = np.squeeze(self.p1, axis=1)
            st = np.squeeze(st)

        # Select good points
        self.good_new = self.p1[st == 1]
        self.good_old = self.p0[st == 1]

        # Now update the previous frame and previous points
        self.old_gray = self.frame_gray.copy()
        self.p0 = self.good_new.reshape(-1, 1, 2)

        self.location = (np.squeeze(self.p0[0]) if self.p0.shape[0] > 0
            else np.array([-1, -1], np.float32))
