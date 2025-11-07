import cv2
from streamlit_webrtc import VideoTransformerBase
from apply_filters import filters

class VideoProcessor(VideoTransformerBase):
    def __init__(self):
        self.selected_filter = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        if self.selected_filter and self.selected_filter in filters:
            img = filters[self.selected_filter]["func"](img)
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return img
