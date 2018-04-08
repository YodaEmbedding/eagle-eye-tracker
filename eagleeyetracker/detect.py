import cv2
import numpy as np

# TODO rename class... this isn't really a detector!
# TODO rename old_gray? gray_prev?
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
        self.old_gray = None
        self.pixel_location = np.array([-1, -1], np.float32)

    def __setattr__(self, name, value):
        if name == 'pixel_location':
            self.location = self._calc_location(value)
            # TODO default value

        super().__setattr__(name, value)

    def next(self, frame):
        self.frame = frame
        self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        self._track_more_points()

        if self.old_gray is None:
            self.old_gray = self.frame_gray
            return

        if self.features.shape[0] == 0:
            self.pixel_location = np.array([-1, -1], np.float32)
            return

        self.features_prev = self.features
        self.features, self.st, err = cv2.calcOpticalFlowPyrLK(self.old_gray,
            self.frame_gray, self.features_prev, None, **self.lk_params)

        self.features = _normalize_arr(self.features, (-1, 2))
        self.st       = _normalize_arr(self.st, -1)

        # Filter bad features
        good_features = self.st == 1
        self.features = self.features[good_features]
        self.features_prev = self.features_prev[good_features]

        self._track_more_points()

        # Update previous frame and points
        self.old_gray = self.frame_gray.copy()

        # Use first point
        self.pixel_location = (self.features[0]
            if self.features.shape[0] > 0
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

    def _track_more_points(self):
        """Append more good features"""

        if self.features.shape[0] >= self.feature_params['maxCorners']:
            return

        new_pts = cv2.goodFeaturesToTrack(self.frame_gray, mask = None,
            **self.feature_params)
        new_pts = _normalize_arr(new_pts, (-1, 2))
        new_pts = new_pts[:self.feature_params['maxCorners'] - self.features.shape[0]]

        self.features = np.vstack([self.features, new_pts])

def _normalize_arr(arr, shape):
    """Normalize given array

    Necessary since OpenCV is weird."""

    return (arr.reshape(shape)
        if arr is not None
        else np.zeros(shape, np.float32))

