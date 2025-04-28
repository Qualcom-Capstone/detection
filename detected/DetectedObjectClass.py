"""
탐지된 객체(DetectedObject)를 정의
"""

from detection.coords import CoordinateClass

"""
label: 객체 라벨 (예: 'car', 'truck', 'person' 등)
coord: Coordinate 객체 (x, y, w, h)
timestamp: 탐지된 시간 (초 단위 float)
"""


class DetectedObject:
    def __init__(self, label: str, coord: CoordinateClass, timestamp: float):
        self.label = label
        self.coord = coord
        self.timestamp = timestamp
        self.id = None  # 트래킹 ID (처음에는 None)

    # 객체에 트래킹 ID부여
    def assign_id(self, obj_id: int):
        self.id = obj_id

    # 바운딩박스 중심좌표 반환
    def get_center(self):
        return self.coord.center()

    # 바운딩박스 면적 반환
    def get_area(self):
        return self.coord.area()
