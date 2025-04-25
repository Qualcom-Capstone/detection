#!/usr/bin/env python3
import os, gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Wayland 환경 설정
os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
os.environ["WAYLAND_DISPLAY"] = "wayland-1"

# GStreamer 초기화
gst = Gst
Gst.init(None)

# GStreamer 파이프라인 정의:
# 1) 카메라 스트림(qtiqmmfsrc)
# 2) tee로 분기하여
#    • 비디오+메타 합성을 위해 qtimetamux/mux → qtioverlay → waylandsink 출력
#    • inference 분기에서 qtimlvdetection 텍스트를 mux에 연결
pipeline_str = (
    'qtiqmmfsrc camera=0 ! '
    'video/x-raw(memory:GBM),format=NV12,width=1920,height=1080,framerate=30/1 ! '
    'tee name=t '
    't. ! queue ! qtimetamux name=mux ! qtioverlay ! waylandsink fullscreen=true sync=false '
    't. ! queue ! qtivtransform ! qtimlvconverter ! '
    'qtimlsnpe delegate=dsp model=/opt/yolonas.dlc layers="</heads/Mul,/heads/Sigmoid>" ! '
    'qtimlvdetection module=yolo-nas labels=/opt/yolonas.labels threshold=51.0 results=10 ! '
    'text/x-raw ! mux.'
)

# 파이프라인 생성 및 실행
pipeline = Gst.parse_launch(pipeline_str)
pipeline.set_state(Gst.State.PLAYING)

# 메인 루프
loop = GLib.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    pipeline.set_state(Gst.State.NULL)
