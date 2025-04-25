import cv2
import numpy as np


# BGR프레임을 HSV색공간으로 변환
def convert_to_hsv(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

