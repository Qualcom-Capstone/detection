import threading
import time
from manager import camera_manager
from s3_uploader import s3_upload
from shared import shared_queue
from gi.repository import Gst, GLib
from http_request import request2server
from shared.line import FRAME_WIDTH, FRAME_HEIGHT

_thread_started = False


def save_and_send(frame_sink):
    while True:
        try:
            flag = shared_queue.shotFlagQueue.get()  # 큐에서 프레임 꺼냄
            meta_item = shared_queue.metaQueue.get()  # 큐에서 메타데이터 꺼냄

            if flag != "TAKE_SHOT" or not meta_item:
                continue

            take_snapshot(frame_sink, meta_item)
            time.sleep(1)

            img_path = f"/home/root/detection/images/car_{meta_item['id']}.jpg"
            s3_meta = s3_upload.upload_image_to_cars_folder(img_path)  # 찍은 이미지 s3서버로 전송


            x = round(meta_item['coord'].x, 3)
            y = round(meta_item['coord'].y, 3)
            w = round(meta_item['coord'].w, 3)
            h = round(meta_item['coord'].h, 3)

            print(f"url : {s3_meta['s3_url']}")
            print(f"key : {s3_meta['s3_key']}")
            print(x)
            print(y)
            print(w)
            print(h)


            data = {
                "image_url": s3_meta['s3_url'],
                "s3_key": s3_meta['s3_key'],
                "car_speed": int(meta_item['over_speed']),
                "x": x,
                "y": y,
                "w": w,
                "h": h
            }
            print("이제 보냄")
            request2server.send_to_server(data)  # 메타 정보 서버로 보냄
            # print(data)

            print("--------------------------------------------")
            print(f"ID: {meta_item['id']} 차량 속도 위반")
            print(f"car_{meta_item['id']}.jpg 서버 전송 완료.")
            print(
                f"x: {data['x']}, y: {data['y']}, w: {data['w']}, h: {data['h']} 속도: {data['car_speed']} 메타 서버 전송 완료.")
            print("--------------------------------------------")

        except Exception as e:
            print(f"Save and Send Thread Error! : {e}")


def take_snapshot(frame_sink, meta_item):
    done_event = threading.Event()

    def wrapped():
        camera_manager.take_screenshot(frame_sink, meta_item['id'])
        done_event.set()
        return False

    GLib.idle_add(wrapped)


def run_save_and_send_thread():
    time.sleep(1)
    global _thread_started
    if _thread_started:
        return

    threading.Thread(target=save_and_send, daemon=True, name="SaveAndSendThread").start()
    _thread_started = True
