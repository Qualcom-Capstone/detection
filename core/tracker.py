import time
from coords.Coordinate import Coordinate
from detected.DetectedObject import DetectedObject
from utils import iou, object_id
from core import speed

tracked_objects = []
IOU_THRESHOLD = 0.5


def track_object(detections):
    current_frame_objects = []
    global tracked_objects

    for obj in detections:  # 객체들을 하나씩 꺼냄
        coords = Coordinate(obj["x"], obj["y"], obj["w"], obj["h"])  # 딕셔너리에서 좌표값 뽑아옴
        detected = DetectedObject(label=obj["label"], coord=coords, timestamp=time.time())  # 감지 객체 생성

        matched = False
        for tracked in tracked_objects:  # 이전 프레임까지 트래킹된 객체들을 하나씩 꺼냄
            # iou계산
            iou_val = iou.compute_iou((detected.coord.x, detected.coord.y, detected.coord.w, detected.coord.h),
                                      (tracked.coord.x, tracked.coord.y, tracked.coord.w, tracked.coord.h))

            if iou_val > IOU_THRESHOLD:  # iou_val이 0.8을 넘기면, 같은 객체로 판단
                detected.id = tracked.id  # 같은 객체니까 id유지
                matched = True
                break  # 같은 객체인거 발견!

        if not matched:
            detected.id = object_id.assign_id()

        speed_val = speed.compute_speed(detected.id, detected.coord, detected.timestamp)  # 해당 id에 대한 속도 계산
        speed.latest_speeds[detected.id] = speed_val
        current_frame_objects.append(detected)

        print(
            f"id={detected.id}, "
            f"speed={'{:.2f}'.format(speed_val) if speed_val is not None else 'None'}, "
            f"x={detected.coord.x:.1f}, y={detected.coord.y:.1f}, "
            f"w={detected.coord.w:.1f}, h={detected.coord.h:.1f}"
        )

    tracked_objects = current_frame_objects
