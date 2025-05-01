"""
프로그램 실행시,
python main.py 2>/dev/null (shell파일로 만들것)
GStreamer관련 출력들 차단함
"""
import sys, os, gi, re
import time
from gi.repository import Gst, GLib
from coords.Coordinate import Coordinate
from detected.DetectedObject import DetectedObject
from parser import meta_parser
from pipeline_config import pipeline_config
from utils import iou
from utils import object_id

gi.require_version('Gst', '1.0')

# Wayland 환경 설정
os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
os.environ["WAYLAND_DISPLAY"] = "wayland-1"

# GStreamer 초기화
Gst.init(None)

PIPELINE_STR = pipeline_config.get_pipeline()

# 파이프라인 생성 및 실행
pipeline = Gst.parse_launch(PIPELINE_STR)
pipeline.set_state(Gst.State.PLAYING)

tracked_objects = []  # 이전 프레임까지 트래킹된 객체들 저장
IOU_THRESHOLD = 0.7  # 같은 객체로 간주할 iou


# appsink 콜백: 메타데이터 출력
def on_meta(sink, _):
    sample = sink.emit('pull-sample')

    if not sample:
        return Gst.FlowReturn.ERROR

    buf = sample.get_buffer()

    global tracked_objects

    try:
        txt = buf.extract_dup(0, buf.get_size())
        raw_txt = txt.decode().strip()
        detections = meta_parser.parse_metadata(raw_txt)  # 객체 탐지 결과를, 딕셔너리가 담긴 리스트로 반환
        current_frame_objects = []

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
                    break # 같은 객체인거 발견!

            if not matched:
                detected.id = object_id.assign_id()

            current_frame_objects.append(detected)

            print(
                f"id={detected.id}, x={detected.coord.x}, y={detected.coord.y}, w={detected.coord.w}, h={detected.coord.h}")

        tracked_objects = current_frame_objects
    except ValueError:
        print("ERROR at extract metadata")

    return Gst.FlowReturn.OK


# meta_sink에 콜백 연결
meta_sink = pipeline.get_by_name('meta_sink')
meta_sink.connect('new-sample', on_meta, None)

# 메인 루프 실행
loop = GLib.MainLoop()

try:
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    pipeline.set_state(Gst.State.NULL)
    print('Pipeline stopped.')
