# from math import sqrt
#
# pre_positions = {}  # id에 대한 (x, y)중심좌표
# pre_timestamps = {}  # id에 대한 timestamp (초 단위 시간)
# latest_speeds = {}  # id에 대한 가장 최근 속도
#
#
# def compute_speed(id, coord, timestamp):
#     cx, cy = coord.center()  # 중심좌표 구함
#     speed = None
#
#     if id in pre_positions:
#         px, py = pre_positions[id]  # 이전의 중심좌표, 시간 불러옴
#         pt = pre_timestamps[id]
#         dt = timestamp - pt  # 시간 차이 (현재시간 - 이전시간)
#
#         # 피타고라스의 법칙으로 이동거리 구함
#         if dt > 0:
#             distance = sqrt((cx - px) ** 2 + (cy - py) ** 2)
#             speed = distance / dt  # 이동거리 / 시간 = 속도
#
#     pre_positions[id] = (cx, cy)
#     pre_timestamps[id] = timestamp
#
#     if speed is not None:
#         latest_speeds[id] = speed  # 특정 id에 대한 속도를 저장
#
#     return speed
#
#
# def compute_and_store_speed(detect_id, detected_coord, detected_timestamp):
#     speed_val = compute_speed(detect_id, detected_coord, detected_timestamp)  # 해당 id에 대한 속도 계산
#     latest_speeds[detect_id] = speed_val  # 해당 id에 대한 속도를 배열로 저장(id를 인덱스로 접근)
#     return speed_val
