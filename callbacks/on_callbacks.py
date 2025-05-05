import sys, os, gi, re
from gi.repository import Gst, GLib
from parser import meta_parser
from core import tracker


# appsink 콜백: 메타데이터 출력
def on_meta(sink, _):
    sample = sink.emit('pull-sample')

    if not sample:
        return Gst.FlowReturn.ERROR

    buf = sample.get_buffer()  # appsink에서 버퍼 받음

    try:
        txt = buf.extract_dup(0, buf.get_size())  # 버퍼에서 메타데이터 뽑아냄
        raw_txt = txt.decode().strip()
        detections = meta_parser.parse_metadata(raw_txt)  # 메타데이터를 객체의 필드에 각각 파싱함 -> 객체 딕셔너리 반환
        tracker.track_object(detections)  # 객체들 트래킹 시작
    except ValueError:
        print("ERROR at extract metadata")

    return Gst.FlowReturn.OK
