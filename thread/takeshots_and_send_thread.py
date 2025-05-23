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
            flag = shared_queue.imageQueue.get()  # 큐에서 프레임 꺼냄
            meta_item = shared_queue.metaQueue.get()  # 큐에서 메타데이터 꺼냄

            if flag != "TAKE_SHOT" or not meta_item:
                continue

            GLib.idle_add(camera_manager.take_screenshot, frame_sink, meta_item['id'])
            time.sleep(2)

            img_path = f"/home/root/detection/images/car_{meta_item['id']}.jpg"
            s3_upload.upload_image_to_cars_folder(img_path)  # 찍은 이미지 s3서버로 전송

            x = meta_item['coord'].x * FRAME_WIDTH  # 바운딩박스의 중앙좌표 x (픽셀단위)
            y = meta_item['coord'].y * FRAME_HEIGHT  # 바운딩박스의 중앙좌표 y
            w = meta_item['coord'].w * FRAME_WIDTH
            h = meta_item['coord'].h * FRAME_HEIGHT

            data = {
                "image_url": f"https://your-bucket.s3.ap-northeast-2.amazonaws.com/images/car_{meta_item['id']}.jpg",
                "s3_key": f"images/car_{meta_item['id']}",
                "car_speed": meta_item['over_speed'],
                "car_id": meta_item['id'],
                "x": x,
                "y": y,
                "w": w,
                "h": h
            }

            request2server.send_to_server(data)  # 메타 정보 서버로 보냄

            print("--------------------------------------------")
            print(f"ID: {meta_item['id']} 차량 속도 위반")
            print(f"car_{meta_item['id']} 서버 전송 완료.")
            print("메타 정보 서버 전송 완료.")
            print("--------------------------------------------")

        except Exception as e:
            print(f"Save and Send Thread Error! : {e}")


def run_save_and_send_thread():
    time.sleep(1)
    global _thread_started
    if _thread_started:
        return

    threading.Thread(target=save_and_send, daemon=True, name="SaveAndSendThread").start()
    _thread_started = True
