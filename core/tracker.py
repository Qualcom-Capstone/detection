import threading
import time
from coords.Coordinate import Coordinate
from detected.DetectedObject import DetectedObject
from utils import iou, object_id
from core import speed
from shared import speed_limit, violation_filter
from s3_uploader import s3_upload
from manager import camera_manager
from shared import shared_queue
import main

tracked_objects = []
IOU_THRESHOLD = 0.5  # 필요시 조정


def track_object(detections):
    current_frame_objects = []  # 현재 프레임에 잡힌 객체 리스트
    global tracked_objects

    for obj in detections:  # 객체들을 하나씩 꺼냄
        coords = Coordinate(obj["x"], obj["y"], obj["w"], obj["h"])  # 각 객체의 좌표(x,y,w,h)로 좌표 객체 생성
        detected = DetectedObject(label=obj["label"], coord=coords, timestamp=time.time())  # 이를 기반으로 감지된 객체 생성

        matched_id = iou.is_iou_match(detected, tracked_objects, IOU_THRESHOLD)  # iou계산하고, 매칭되는 id있는지 확인

        if matched_id is not None:  # 매칭 id 찾음
            detected.id = matched_id
        else:  # 못찾음 -> 새로 할당
            detected.id = object_id.assign_id()

        speed_val = speed.compute_and_store_speed(detected.id, detected.coord, detected.timestamp)  # 속도 계산 및 저장

        if speed_val > speed_limit.SPEED_LIMIT:  # 과속 했다면
            is_ok = violation_filter.should_send_violation(detected.id)  # 보내도 되는지 확인 (이전에 이미 단속된 차량인지)
            if is_ok:
                violation_info = {
                    'time': detected.timestamp,
                    'over_speed': speed_val,
                    'id': detected.id,
                    'coord': detected.coord
                }
                shared_queue.imageQueue.put(main.frame_sink)  # 과속한 순간의 프레임, 큐에 넣음
                shared_queue.metaQueue.put(violation_info)  # 과속한 순간의 메타데이터, 큐에 넣음

        current_frame_objects.append(detected)  # 현재 프레임에, 생성했던 객체 넣음

        print(
            f"id={detected.id}, "
            f"speed={'{:.2f}'.format(speed_val) if speed_val is not None else 'None'}, "
            f"x={detected.coord.x:.1f}, y={detected.coord.y:.1f}, "
            f"w={detected.coord.w:.1f}, h={detected.coord.h:.1f}"
        )

    tracked_objects = current_frame_objects  # 다음 프레임 비교를 위해 현재 프레임 객체들을 트래킹 리스트로 갱신
