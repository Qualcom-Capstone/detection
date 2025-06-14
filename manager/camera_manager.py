import sys, os, gi, re
from gi.repository import Gst, GLib
from utils.save_image import save_raw_frame_as_jpeg
import time


def take_screenshot(frame_sink, car_id):
    print("[INFO] 사진 촬영중...")

    try:
        sample = frame_sink.emit("pull-sample")
        if not sample:
            print("[ERROR] No frame received.")
            return

        buffer = sample.get_buffer()
        if not buffer:
            print("[ERROR] No buffer in sample")
            return

        success, map_info = buffer.map(Gst.MapFlags.READ)
        if not success:
            print("[ERROR] Buffer mapping failed.")
            return

        try:
            frame_bytes = bytes(map_info.data)
            caps_str = sample.get_caps().to_string()
            print("[DEBUG] sample caps:", caps_str)
            filename = f"/home/root/detection/images/car_{car_id}.jpg"
            save_raw_frame_as_jpeg(frame_bytes, filename)
            print("[INFO] 촬영 완료!")
        finally:
            buffer.unmap(map_info)
    except Exception as e:
        print(f"[EXCEPTION] take_snapshot: {e}")
