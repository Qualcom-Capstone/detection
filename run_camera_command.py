import os, gi, re

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Wayland 환경 설정
os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
os.environ["WAYLAND_DISPLAY"] = "wayland-1"

# GStreamer 초기화
Gst.init(None)

pipeline_str = (
    'qtiqmmfsrc camera=0 ! '
    'video/x-raw(memory:GBM),format=NV12,width=1920,height=1080,framerate=30/1 ! '
    'tee name=t '
    # 화면 출력용 분기: mux→overlay→waylandsink
    't. ! queue ! qtimetamux name=mux ! qtioverlay ! waylandsink fullscreen=true sync=false '
    # inference 분기: 메타데이터 추출 및 mux로 전달
    't. ! queue ! qtivtransform ! qtimlvconverter ! '
    'qtimlsnpe delegate=dsp model=/opt/yolonas.dlc layers="</heads/Mul,/heads/Sigmoid>" ! '
    'qtimlvdetection module=yolo-nas labels=/opt/yolonas.labels threshold=51.0 results=10 ! '
    'text/x-raw ! tee name=mt '
    # mux 입력, appsink으로 메타 가져오기
    'mt. ! queue ! mux. '
    'mt. ! queue ! appsink name=meta_sink emit-signals=true sync=false drop=true max-buffers=1'
)

# 파이프라인 생성 및 실행
pipeline = Gst.parse_launch(pipeline_str)
pipeline.set_state(Gst.State.PLAYING)


# 메타데이터 파싱 함수
def parse_metadata(txt):
    cleaned = txt.replace('\\', '')
    m = re.search(r'bounding-boxes=\(structure\)<(.*?)>,\s*timestamp', cleaned, re.DOTALL)
    if m:
        content = m.group(1)
        entries = re.findall(r'"(.*?)"', content)
        for entry in entries:
            print(entry)  # 라벨 및 좌표 출력
    else:
        print(txt)


# appsink 콜백
def on_meta(sink, _):
    sample = sink.emit('pull-sample')
    buf = sample.get_buffer()
    data = buf.extract_dup(0, buf.get_size())
    txt = data.decode('utf-8').strip()
    parse_metadata(txt)
    return Gst.FlowReturn.OK


# meta_sink 연결
meta_sink = pipeline.get_by_name('meta_sink')
meta_sink.connect('new-sample', on_meta, None)

# GLib 메인 루프
loop = GLib.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    pipeline.set_state(Gst.State.NULL)
