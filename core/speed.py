from shared import line
import time


def record_y1_pass_time(id):
    line.y1_pass_time[id] = time.time()


def record_y2_pass_time(id):
    line.y2_pass_time[id] = time.time()


def compute_speed(id):
    t = line.y2_pass_time[id] - line.y1_pass_time[id]
    speed = line.REAL_DISTANCE / t * 3.6  # m/s -> km/h 변환
    return speed
