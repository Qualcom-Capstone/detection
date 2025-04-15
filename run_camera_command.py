"""
이 파일은,

export XDG_RUNTIME_DIR=/dev/socket/weston
export WAYLAND_DISPLAY=wayland-1
setprop persist.overlay.use_c2d_blit 2
gst-launch-1.0 -e --gst-debug=1 qtiqmmfsrc name=camsrc camera=0 ! video/x-raw\(memory:GBM\),format=NV12,width=1280,height=720,framerate=30/1,compression=ubwc ! queue ! tee name=split split. ! queue ! qtivcomposer name=mixer sink_1::dimensions="<1920,1080>" ! queue ! waylandsink fullscreen=true sync=true split. ! queue ! qtimlvconverter ! queue ! qtimlsnpe delegate=dsp model=/opt/yolonas.dlc layers="</heads/Mul, /heads/Sigmoid>" ! queue ! qtimlvdetection threshold=51.0 results=10 module=yolo-nas labels=/opt/yolonas.labels ! video/x-raw,width=640,height=360 ! queue ! mixer.

QIM모델을 실행할때 필요한 명령어 입력들을 스크립트로 자동화 시켜 놓은 파일임.
"""
import subprocess
import os
import cv2


def run_command(command):
    """주어진 명령어를 실행하고, 성공 여부를 반환"""
    try:
        print(f"Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # 표준 출력과 에러 출력 출력
        if stdout:
            print(stdout.decode())
        if stderr:
            print(stderr.decode())

        if process.returncode != 0:
            print(f"Error: Command failed with return code {process.returncode}")
            return False
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def run_gstreamer_pipeline():
    # 시스템 속성 설정
    run_command("setprop persist.overlay.use_c2d_blit 2")

    # GStreamer 파이프라인
    gst_pipeline = (
        "qtiqmmfsrc name=camsrc camera=0 ! "
        "video/x-raw(memory:GBM),format=NV12,width=1920,height=1080,framerate=30/1,compression=ubwc ! "
        "tee name=t "
        "t. ! queue ! qtivcomposer ! waylandsink fullscreen=false render-rectangle=\"0,0,960,1080\" "
        "t. ! queue ! qtimlvconverter ! "
        "qtimlsnpe delegate=dsp model=/opt/yolonas.dlc layers=\"</heads/Mul, /heads/Sigmoid>\" ! "
        "qtimlvdetection threshold=51.0 results=10 module=yolo-nas labels=/opt/yolonas.labels ! "
        "qtivoverlay ! videoconvert ! video/x-raw,format=BGR ! appsink"
    )

    # openCV로 GStreamer파이프라인 열기
    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print("GStreamer 파이프라인 열기 실패")
        return

    print("OpenCV가 GStreamer 파이프라인에서 프레임을 가져오는중...")
    cv2.namedWindow("Detection via OpenCV", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Detection via OpenCV", 960, 1080)
    cv2.moveWindow("OpenCV Detection", 960, 0)

    while True:
        ret, frame = cap.read()  # ret: 성공여부, frame: 읽어온 프레임
        if not ret:
            print("프레임 수신 실패")
            break

        cv2.imshow("Detection via OpenCV", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 키입력 기다리다가 'q'입력받으면 루프 종료
            break

    cap.release()
    cv2.destroyAllWindows()


def run_all_commands():
    # 환경 변수 설정 - 한 번만 설정
    os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
    os.environ["WAYLAND_DISPLAY"] = "wayland-1"

    # GStreamer 파이프라인 직접 실행
    run_gstreamer_pipeline()


# 모든 명령어 실행
if __name__ == "__main__":
    run_all_commands()
