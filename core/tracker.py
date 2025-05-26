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
from shared import line
from shared.speed_limit import SPEED_LIMIT

tracked_objects = []
IOU_THRESHOLD = 0.4  # 필요시 조정


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

        car_bbox_bottom = detected.coord.bottom() * line.FRAME_HEIGHT  # 차량의 바운딩박스 하단 좌표를 관찰
        speed_val = None
        if car_bbox_bottom >= line.LINE_Y1 and detected.id not in line.y1_pass_time:  # y1 라인을 통과할 때, 시간 기록
            speed.record_y1_pass_time(detected.id)
            print(f"차량 id={detected.id}가 y1통과")

        if car_bbox_bottom >= line.LINE_Y2 and detected.id not in line.y2_pass_time:  # y2 라인을 통과할 때, 시간 기록
            speed.record_y2_pass_time(detected.id)
            speed_val = speed.compute_speed(detected.id)  # 구간에서의 속도를 측정
            print(f"차량 id={detected.id}가 y2통과")

        if speed_val is not None and speed_val > SPEED_LIMIT:  # 속도가 초과 했을 때
            print(f"[🚨 과속] 차량 id={detected.id}, Speed={speed_val:.2f} km/h (제한속도: {SPEED_LIMIT} km/h)")
            is_ok = violation_filter.should_send_violation(detected.id)  # 보내도 되는지 확인 (이전에 이미 단속된 차량인지)
            if is_ok:
                violation_info = {
                    'over_speed': speed_val,
                    'id': detected.id,
                    'coord': detected.coord
                }
                shared_queue.shotFlagQueue.put("TAKE_SHOT")  # 과속한 순간 신호 전달
                shared_queue.metaQueue.put(violation_info)  # 과속한 순간의 메타데이터, 큐에 넣음
        elif speed_val is not None and speed_val <= SPEED_LIMIT:
            print(f"[✅ 정상] 차량 id={detected.id}, Speed={speed_val:.2f} km/h (제한속도: {SPEED_LIMIT} km/h)")

        current_frame_objects.append(detected)  # 현재 프레임에, 생성했던 객체 넣음

    tracked_objects = current_frame_objects  # 다음 프레임 비교를 위해 현재 프레임 객체들을 트래킹 리스트로 갱신
