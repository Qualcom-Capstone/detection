import threading
import time
from shared import shared_queue
from core import tracker

_thread_started = False


def postprocess_thread():
    while True:
        try:
            detections = shared_queue.detectionQueue.get()
            if not detections:
                # print("empty queue!")
                continue

            tracker.track_object(detections)
        except Exception as e:
            print(f"PostProcessThread Error!! : {e}")


def run_thread():
    time.sleep(2)
    global _thread_started
    if _thread_started:  # 스레드 실행했다면
        return

    threading.Thread(target=postprocess_thread, daemon=True, name="PostProcessThread").start()
    _thread_started = True
