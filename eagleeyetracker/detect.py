import cv2
import numpy as np

# TODO rename class... this isn't really a detector!
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

        self.features      = np.zeros((0, 2), np.float32)
        self.features_prev = np.zeros((0, 2), np.float32)
        self.frame_gray_prev = None
        self.pixel_location = None

    def __setattr__(self, name, value):
        if name == 'pixel_location':
            self.location = self._calc_location(value)
            if value is None:
                value = np.array([-1, -1], np.float32)

        cv_arrs = {
            'features_new': (-1, 2),
            'features': (-1, 2),
            'st': -1
        }

        if name in cv_arrs:
            value = _normalize_arr(value, cv_arrs[name])

        super().__setattr__(name, value)

    def next(self, frame):
        self.frame = frame
        self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        self._track_more_points()

        if self.frame_gray_prev is None:
            self.frame_gray_prev = self.frame_gray
            return

        if self.features.shape[0] == 0:
            self.pixel_location = None
            return

        self.features_prev = self.features
        self.features, self.st, err = cv2.calcOpticalFlowPyrLK(
            self.frame_gray_prev, self.frame_gray,
            self.features_prev, None, **self.lk_params)

        # Filter bad features
        good_features = self.st == 1
        self.features = self.features[good_features]
        self.features_prev = self.features_prev[good_features]

        self._track_more_points()

        # Update previous frame and points
        self.frame_gray_prev = self.frame_gray.copy()

        # Use first point
        self.pixel_location = (self.features[0]
            if self.features.shape[0] > 0
            else None)

    def _calc_location(self, pixel_location):
        """Offset and normalize location (x. y) within range [-1, 1]"""

        if pixel_location is None:
            return (0, 0)

        size = np.flip(self.frame.shape[0:2], axis=0)
        scale = 2. / np.max(size)
        offset = 0.5 * np.array(size)
        coords = scale * (pixel_location - offset)
        return (coords[0], -coords[1])

    def _track_more_points(self):
        """Append more good features"""

        if self.features.shape[0] >= self.feature_params['maxCorners']:
            return

        self.features_new = cv2.goodFeaturesToTrack(self.frame_gray,
            mask = None, **self.feature_params)
        size_new = self.feature_params['maxCorners'] - self.features.shape[0]
        self.features_new = self.features_new[:size_new]

        self.features = np.vstack([self.features, self.features_new])

def _normalize_arr(arr, shape):
    """Normalize given array

    Necessary since OpenCV is weird."""

    return (arr.reshape(shape)
        if arr is not None
        else np.zeros(shape, np.float32))

