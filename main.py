"""
프로그램 실행시,
python main.py 2>/dev/null (shell파일로 만들것)
GStreamer관련 출력들 차단함
"""
import sys, os, gi, re
from gi.repository import Gst, GLib
from pipeline_config import pipeline_config
from callbacks import on_callbacks
import threading, time
from utils.save_image import save_raw_frame_as_jpeg
from manager import camera_manager

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

# 실행 10초 후 자동 저장 (for test), 이건 테스트용도임. 필요에 따라 함수 호출하면 됨.
threading.Timer(10, lambda: camera_manager.take_screenshot(frame_sink)).start()

# 메인 루프 실행
loop = GLib.MainLoop()

try:
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    pipeline.set_state(Gst.State.NULL)
    print('Pipeline stopped.')
