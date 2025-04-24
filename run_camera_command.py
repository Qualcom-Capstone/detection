#!/usr/bin/env python3
import os, gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# 1) GStreamer 초기화
Gst.init(None)

# 2) Wayland 환경 변수 및 overlay 최적화
os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
os.environ["WAYLAND_DISPLAY"] = "wayland-1"
os.system("setprop persist.overlay.use_c2d_blit 2")

# 3) 파이프라인 정의 (꺽쇠(<>) 포함)
pipeline_str = (
    "qtiqmmfsrc name=camsrc camera=0 ! "
    "video/x-raw(memory:GBM),format=NV12,width=1280,height=720,framerate=30/1 ! "
    "tee name=split "
    "split. ! queue ! qtivtransform ! "
    "waylandsink fullscreen=true sync=false "
    "split. ! queue ! qtivtransform ! "
    "qtimlvconverter ! "
    "qtimlsnpe delegate=dsp model=/opt/yolonas.dlc layers=\"</heads/Mul,/heads/Sigmoid>\" ! "
    "qtimlvdetection threshold=51.0 results=10 module=yolo-nas labels=/opt/yolonas.labels ! "
    "tee name=dettee "
    "dettee. ! queue ! fakesink "
    "dettee. ! queue ! text/x-raw,format=utf8 ! appsink name=meta_sink emit-signals=true drop=true"
)

print("▶ Using pipeline:\n", pipeline_str)

# 4) 파이프라인 빌드
pipeline = Gst.parse_launch(pipeline_str)


def on_meta(sink):
    sample = sink.emit("pull-sample")
    if not sample:
        return Gst.FlowReturn.ERROR
    buf = sample.get_buffer()

    # extract_dup 함수 수정
    try:
        # 새로운 API 방식 (여러 값 반환)
        data = buf.extract_dup(0, buf.get_size())
        print("[METADATA]", data.decode().strip())
    except ValueError:
        # 이전 API 방식 (튜플 반환)
        result = buf.extract_dup(0, buf.get_size())
        if isinstance(result, tuple):
            ok, data = result
            if ok:
                print("[METADATA]", data.decode().strip())

    return Gst.FlowReturn.OK


meta = pipeline.get_by_name("meta_sink")
meta.connect("new-sample", on_meta)

# 6) 실행
pipeline.set_state(Gst.State.PLAYING)
try:
    GLib.MainLoop().run()
except KeyboardInterrupt:
    pass
finally:
    pipeline.set_state(Gst.State.NULL)
