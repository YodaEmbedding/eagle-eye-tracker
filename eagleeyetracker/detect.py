import cv2
import numpy as np

# TODO rename class... this isn't really a detector!
# TODO rename variables, e.g. good_new
class Detector(object):
    def __init__(self):
        self.feature_params = dict(
            maxCorners=4,
            qualityLevel=0.3,
            minDistance=7,
            blockSize=7)

        self.lk_params = dict(
            winSize=(15,15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        self.pixel_location = np.array([-1, -1], np.float32)
        self.good_old = np.zeros((0, 2), np.float32)
        self.good_new = np.zeros((0, 2), np.float32)
        self.old_gray = None
        self.p0 = np.array([], np.float32).reshape(0, 1, 2)

    def __setattr__(self, name, value):
        if name == 'pixel_location':
            self.location = self._calc_location(value)

        super().__setattr__(name, value)

    def next(self, frame):
        self.frame = frame
        self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        self._track_more_points()

        if self.old_gray is None:
            self.old_gray = self.frame_gray
            return

        if self.p0.shape[0] == 0:
            self.pixel_location = np.array([-1, -1], np.float32)
            return

        self.p1, self.st, err = cv2.calcOpticalFlowPyrLK(self.old_gray,
            self.frame_gray, self.p0, None, **self.lk_params)

        self._normalize_data()

        # Filter bad points
        self.good_new = self.p1[self.st == 1]
        self.good_old = self.p0[self.st == 1]

        # Center
        #self.p1[self.st == 1] = ...
        #self.good_new = self.p1
        #self.good_old = self.p0

        self._track_more_points()

        # Update previous frame and points
        self.old_gray = self.frame_gray.copy()
        self.p0 = self.good_new.reshape(-1, 1, 2)

        # Use first point
        self.pixel_location = (np.squeeze(self.p0[0])
            if self.p0.shape[0] > 0
            else np.array([-1, -1], np.float32))

    def _calc_location(self, pixel_location):
        """Offset and normalize location (x. y) within range [-1, 1]"""

        if np.any(pixel_location < 0):
            return (0, 0)

        size = np.flip(self.frame.shape[0:2], axis=0)
        scale = 2. / np.max(size)
        offset = 0.5 * np.array(size)
        coords = scale * (pixel_location - offset)
        return (coords[0], -coords[1])

    def _normalize_data(self):
        """Normalize p1 and st

        Necessary since OpenCV is weird."""

        if self.p1 is None:
            self.p1 = np.zeros((0, 0), np.float32)
            self.st = np.zeros(0, np.float32)
        else:
            self.p1 = np.squeeze(self.p1, axis=1)
            self.st = np.squeeze(self.st)

    def _track_more_points(self):
        """Append more good features"""

        if self.p0.shape[0] >= self.feature_params['maxCorners']:
            return

        new_pts = cv2.goodFeaturesToTrack(self.frame_gray, mask = None,
            **self.feature_params)

        if new_pts is None:
            new_pts = np.array([], np.float32).reshape(0, 1, 2)

        new_pts = new_pts[:self.feature_params['maxCorners'] - self.p0.shape[0]]
        self.p0 = np.vstack([self.p0, new_pts])

