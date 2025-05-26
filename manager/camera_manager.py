import sys, os, gi, re
from gi.repository import Gst, GLib
from utils.save_image import save_raw_frame_as_jpeg
import time


def take_screenshot(frame_sink, car_id):
    print("[INFO] Taking screenshot...")

    sample = frame_sink.emit("pull-sample")
    if not sample:
        print("[ERROR] No frame received.")
        return

    buffer = sample.get_buffer()
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
    finally:
        buffer.unmap(map_info)
