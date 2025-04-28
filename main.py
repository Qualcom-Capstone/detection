"""
프로그램 실행시,
python main.py 2>/dev/null (shell파일로 만들것)
GStreamer관련 출력들 차단함
"""

import sys, os, gi, re
from gi.repository import Gst, GLib
from parser import meta_parser

gi.require_version('Gst', '1.0')

# Wayland 환경 설정
os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
os.environ["WAYLAND_DISPLAY"] = "wayland-1"
# GStreamer 초기화
Gst.init(None)

# 전체 영상에 대해 상하 반전을 inference + display 양쪽에 모두 적용하기 위해
# tee 이전에 qtivtransform flip-vertical=true 삽입
# threshold에 따라서 프레임 드랍 현상 생김 -> 조정 필요
pipeline_str = (
    'qtiqmmfsrc camera=0 ! '
    'qtivtransform flip-vertical=true ! '
    'video/x-raw(memory:GBM),format=NV12,width=1920,height=1080,framerate=30/1 ! '
    'tee name=t '
    't. ! queue ! qtimetamux name=mux ! qtioverlay ! waylandsink fullscreen=true sync=false '
    't. ! queue ! qtimlvconverter ! '
    'qtimlsnpe delegate=dsp model=/opt/yolonas.dlc layers="</heads/Mul,/heads/Sigmoid>" ! '
    'qtimlvdetection module=yolo-nas labels=/opt/yolonas.labels threshold=91.0 results=10 ! '
    'text/x-raw ! tee name=mt '
    'mt. ! queue ! mux. '
    'mt. ! queue ! appsink name=meta_sink emit-signals=true sync=false drop=true max-buffers=1'
)

# 파이프라인 생성 및 실행
pipeline = Gst.parse_launch(pipeline_str)
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
        meta_parser.parse_metadata(raw_txt)
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
