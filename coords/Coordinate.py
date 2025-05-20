"""
좌표 관련한 클래스, 함수 모아 놓은 파일
"""


class Coordinate:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x  # 중심 x (상대 위치임)
        self.y = y  # 중심 y
        self.w = w  # 너비
        self.h = h  # 높이

    # 바운딩박스 중심좌표 반환
    def center(self):
        return self.x, self.y

    # 하단 좌표 반환
    def bottom(self):
        return self.y + self.h / 2

    # 바운딩박스 면적 반환
    def area(self):
        return self.w * self.h
