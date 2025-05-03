import sys, os, gi, re
from gi.repository import Gst, GLib
from parser import meta_parser
from core import tracker


# appsink 콜백: 메타데이터 출력
def on_meta(sink, _):
    sample = sink.emit('pull-sample')

    if not sample:
        return Gst.FlowReturn.ERROR

    buf = sample.get_buffer()

    try:
        txt = buf.extract_dup(0, buf.get_size())
        raw_txt = txt.decode().strip()
        detections = meta_parser.parse_metadata(raw_txt)  # 객체 탐지 결과를, 딕셔너리가 담긴 리스트로 반환
        tracker.track_object(detections)
    except ValueError:
        print("ERROR at extract metadata")

    return Gst.FlowReturn.OK

