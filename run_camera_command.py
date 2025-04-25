#!/usr/bin/env python3
import os, gi, re

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# GStreamer 초기화
Gst.init(None)

# wayland관련 환경변수 세팅
os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
os.environ["WAYLAND_DISPLAY"] = "wayland-1"
os.system("setprop persist.overlay.use_c2d_blit 2")

# 파이프라인 정의
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

# 파이프라인 빌드
pipeline = Gst.parse_launch(pipeline_str)


def parse_metadata(raw_text):
    cleaned = raw_text.encode('utf-8').decode('unicode_escape')
    cleaned = cleaned.replace('\\', '')  # 이스케잎 문자 제거
    # print("[DEBUG CLEANED]", cleaned) # 디버그용

    # bounding-boxes 영역 추출
    bbox_section = re.search(r'bounding-boxes=\(structure\)<(.*?)>,\s*timestamp', cleaned, re.DOTALL)
    if not bbox_section:
        # print("[WARN] bounding-boxes 구조체를 찾을 수 없음.") # 디버그용
        return

    bbox_content = bbox_section.group(1)

    # 객체별 항목 추출 (큰따옴표로 구분된)
    object_entries = re.findall(r'"(.*?)"', bbox_content)

    for obj in object_entries:
        # 라벨
        label_match = re.match(r'([a-zA-Z0-9_.]+)', obj)
        label = label_match.group(1) if label_match else "unknown"

        # 바운딩 박스 추출
        rect_match = re.search(
            r'rectangle=\(float\)<\s*([\d\.\-e]+)\s*,\s*([\d\.\-e]+)\s*,\s*([\d\.\-e]+)\s*,\s*([\d\.\-e]+)\s*>', obj)
        if rect_match:
            x, y, w, h = map(float, rect_match.groups())
            print(f"[DETECTED] label: {label}, bbox: x={x:.3f}, y={y:.3f}, w={w:.3f}, h={h:.3f}")
        else:
            print(f"[DETECTED] label: {label}, but no rectangle found")


def on_meta(sink):
    sample = sink.emit("pull-sample")
    if not sample:
        return Gst.FlowReturn.ERROR
    buf = sample.get_buffer()

    # extract_dup 함수 수정
    try:
        # 새로운 API 방식 (여러 값 반환)
        data = buf.extract_dup(0, buf.get_size())
        raw_text = data.decode().strip()
        parse_metadata(raw_text)
        # print("[METADATA extract_dup1]", data.decode().strip())
    except ValueError:
        # 이전 API 방식 (튜플 반환)
        print("[ERROR at extract]")
        # result = buf.extract_dup(0, buf.get_size())
        # if isinstance(result, tuple):
        #     ok, data = result
        #     if ok:
        #         print("[METADATA extract_dup2]", data.decode().strip())

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
