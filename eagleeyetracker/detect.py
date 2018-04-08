import cv2
import numpy as np

# TODO rename class... this isn't really a detector!
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

        self.pixel_location = np.array([-1, -1], np.float32)
        self._determine_location()
        self.good_old = np.zeros((0, 2), np.float32)
        self.good_new = np.zeros((0, 2), np.float32)
        self.old_gray = None

    # TODO make this a setter for self.pixel_location
    def _determine_location(self):
        if np.any(self.pixel_location < 0):
            self.location = (0, 0)
            return

        size = np.flip(self.frame.shape[0:2], axis=0)
        scale = 2. / np.max(size)
        offset = 0.5 * np.array(size)
        coords = scale * (self.pixel_location - offset)
        self.location = (coords[0], -coords[1])

    def _first_run(self):
        self.p0 = cv2.goodFeaturesToTrack(self.frame_gray, mask = None,
            **self.feature_params)
        # TODO this is a strange way of doing things
        self.p0 = (np.array([], np.float32).reshape(0, 1, 2)
            if self.p0 is None else self.p0)
        self.old_gray = self.frame_gray

    def _track_more_points(self):
        new_pts = cv2.goodFeaturesToTrack(self.frame_gray, mask = None,
            **self.feature_params)
        # TODO eww...
        new_pts = (np.array([], np.float32).reshape(0, 1, 2)
            if new_pts is None else new_pts)
        self.p0 = np.vstack([self.p0, new_pts[:4 - self.p0.shape[0]]])

    def _normalize_data(self):
        """Normalize p1 and st

        Necessary since OpenCV is weird"""
        if self.p1 is None:
            self.p1 = np.zeros((0, 0), np.float32)
            self.st = np.zeros(0, np.float32)
        else:
            self.p1 = np.squeeze(self.p1, axis=1)
            self.st = np.squeeze(self.st)

    def next(self, frame):
        self.frame = frame
        self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        if self.old_gray is None:
            self._first_run()
            return

        if self.p0.shape[0] < 4:
            self._track_more_points()

        # TODO think about what happens when no points at all to track
        if self.p0.shape[0] == 0:
            self.pixel_location = np.array([-1, -1], np.float32)
            self._determine_location()
            return

        self.p1, self.st, err = cv2.calcOpticalFlowPyrLK(self.old_gray,
            self.frame_gray, self.p0, None, **self.lk_params)

        self._normalize_data()

        # Filter bad points
        self.good_new = self.p1[self.st == 1]
        self.good_old = self.p0[self.st == 1]

        # TODO check if this messes things up or not
        # (added randomly by Mateen on a strange whim)
        if self.p0.shape[0] < 4:
            self._track_more_points()

        # Update previous frame and points
        self.old_gray = self.frame_gray.copy()
        self.p0 = self.good_new.reshape(-1, 1, 2)

        # Use first point
        self.pixel_location = (np.squeeze(self.p0[0])
            if self.p0.shape[0] > 0
            else np.array([-1, -1], np.float32))

        self._determine_location()

