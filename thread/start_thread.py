import gi
import threading
import time

from gi.repository import Gst, GLib
from thread.postprocess_thread import tracking_thread
from thread.takeshots_and_send_thread import save_and_send


def start_threads(frame_sink):
    print("[INFO] GLib 루프가 시작되었고, 이제 스레드 시작")

    time.sleep(2)  # 안정화를 위해 2초 대기

    tracking_thread()
    print("[INFO] 트래킹 스레드 실행됨")

    threading.Thread(target=save_and_send, args=(frame_sink,), daemon=True).start()
    print("[INFO] 사진 촬영 및 전송 스레드 실행됨")

    return False  # False를 리턴하면 idle_add가 더 이상 반복 실행 안 함
