"""
좌표 관련한 클래스, 함수 모아 놓은 파일
"""


class Coordinate:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x  # 좌측 상단 x좌표
        self.y = y  # 좌측 상단 y좌표
        self.w = w  # 좌측 상단에서 가로 길이
        self.h = h  # 좌측 상단에서 부터의 세로 길이

    # 바운딩박스 중심좌표 반환
    def center(self):
        center_x = self.x + self.w / 2
        center_y = self.y + self.h / 2
        return center_x, center_y

    # 하단 좌표 반환
    def bottom(self):
        return self.y + self.h

    # 바운딩박스 면적 반환
    def area(self):
        return self.w * self.h
