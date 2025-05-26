"""
프로그램 실행시,
python main.py 2>/dev/null (shell파일로 만들것)
GStreamer관련 출력들 차단함
"""
import os, gi
import threading
import time

from gi.repository import Gst, GLib
from pipeline_config import pipeline_config
from callbacks import on_callbacks
from thread.postprocess_thread import tracking_thread
from thread.takeshots_and_send_thread import save_and_send
from thread.start_thread import start_threads

gi.require_version('Gst', '1.0')

# Wayland 환경 설정
os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
os.environ["WAYLAND_DISPLAY"] = "wayland-1"

# GStreamer 초기화
Gst.init(None)

PIPELINE_STR = pipeline_config.get_pipeline()  # 파이프라인 가져옴

# 파이프라인 생성 및 실행
pipeline = Gst.parse_launch(PIPELINE_STR)
pipeline.set_state(Gst.State.PLAYING)

# meta_sink에 콜백 연결 (메타데이터 추출용)
meta_sink = pipeline.get_by_name('meta_sink')
meta_sink.connect('new-sample', on_callbacks.on_meta, None)

# 스크린샷 찍는 용도
frame_sink = pipeline.get_by_name('frame_sink')

# 메인 루프 실행
loop = GLib.MainLoop()

GLib.idle_add(start_threads, frame_sink)

try:
    print("[INFO] main loop시작")
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    pipeline.set_state(Gst.State.NULL)
    print('Pipeline stopped.')
