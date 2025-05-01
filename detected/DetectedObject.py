"""
탐지된 객체(DetectedObject)를 정의
"""

from coords.Coordinate import Coordinate
from utils import object_id

"""
label: 객체 라벨 (예: 'car', 'truck', 'person' 등)
coord: Coordinate 객체 (x, y, w, h)
timestamp: 탐지된 시간 (초 단위 float)
"""


class DetectedObject:
    def __init__(self, label: str, coord: Coordinate, timestamp: float):
        self.label = label
        self.coord = coord
        self.timestamp = timestamp
        self.id = object_id.assign_id()  # 객체 생성시, 특정 ID를 할당

    # 바운딩박스 중심좌표 반환
    def get_center(self):
        return self.coord.center()

    # 바운딩박스 면적 반환
    def get_area(self):
        return self.coord.area()
