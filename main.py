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


# appsink 콜백: 메타데이터 출력
def on_meta(sink, _):
    sample = sink.emit('pull-sample')

    if not sample:
        return Gst.FlowReturn.ERROR

    buf = sample.get_buffer()

    try:
        txt = buf.extract_dup(0, buf.get_size())
        raw_txt = txt.decode().strip()
        detections = meta_parser.parse_metadata(raw_txt)  # 객체탐지결과 딕셔너리

        for obj in detections:
            coords = Coordinate(obj["x"], obj["y"], obj["w"], obj["h"])  # 좌표 객체
            detected = DetectedObject(label=obj["label"], coord=coords, timestamp=time.time())  # 감지 객체 생성
            print(f"x={detected.coord.x}, y={detected.coord.y}, w={detected.coord.w}, h={detected.coord.h}")

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
