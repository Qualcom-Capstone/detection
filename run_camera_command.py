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
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import threading
import time

# GStreamer 초기화
Gst.init(None)


def meta_callback(meta, user_data):
    print(f"메타데이터 내용: {str(meta)}")
    return True


# appsink에서 샘플을 받았을 때 호출될 콜백 함수
# https://gstreamer.freedesktop.org/documentation/gstreamer/gstsample.html?gi-language=python :Gst.Sample문서 참고
# https://gstreamer.freedesktop.org/documentation/gstreamer/gstbuffer.html?gi-language=python#gst_buffer_foreach_meta :Gst.Buffer문서 참고
def on_new_sample(sink):
    """appsink에서 새 샘플이 도착할 때 호출되는 콜백"""
    sample = sink.emit("pull-sample")  # 여기서 sample은 Gst.Sample객체
    if not sample:
        return Gst.FlowReturn.ERROR

    buffer = sample.get_buffer()  # sample의 버퍼 얻기: Gst.Buffer
    buffer.foreach_meta(meta_callback, None)  # 버퍼 순환시에는 foreach_meta를 사용

    return Gst.FlowReturn.OK


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

    # 파이프라인 문자열 - appsink 추가
    pipeline_str = """
    qtiqmmfsrc name=camsrc camera=0 ! video/x-raw(memory:GBM),format=NV12,width=1920,height=1080,framerate=30/1,compression=ubwc ! 
    queue ! tee name=split 
    split. ! queue ! qtivcomposer name=mixer sink_1::dimensions="<1920,1080>" ! queue ! waylandsink fullscreen=true sync=true 
    split. ! queue ! qtimlvconverter ! queue ! 
    qtimlsnpe delegate=dsp model=/opt/yolonas.dlc layers="</heads/Mul, /heads/Sigmoid>" ! queue ! 
    qtimlvdetection threshold=51.0 results=10 module=yolo-nas labels=/opt/yolonas.labels ! 
    tee name=detect_tee 
    detect_tee. ! queue ! video/x-raw,width=640,height=360 ! queue ! mixer.
    detect_tee. ! queue ! appsink name=detect_sink emit-signals=true
    """

    # 파이프라인 생성
    pipeline = Gst.parse_launch(pipeline_str)

    # appsink 가져오기 및 콜백 연결
    detect_sink = pipeline.get_by_name("detect_sink")
    detect_sink.connect("new-sample", on_new_sample)  # appsink에 데이터가 도착할때마다, on_new_sample실행

    # 버스 이벤트 처리를 위한 메인 루프
    loop = GLib.MainLoop()

    # 버스 연결
    bus = pipeline.get_bus()
    bus.add_signal_watch()

    def on_message(bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            print("End-of-stream")
            loop.quit()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err}: {debug}")
            loop.quit()
        return True

    bus.connect("message", on_message)

    # 파이프라인 시작
    pipeline.set_state(Gst.State.PLAYING)
    print("파이프라인이 시작되었습니다.")

    try:
        # 별도 스레드에서 GLib 메인 루프 실행
        thread = threading.Thread(target=loop.run)
        thread.daemon = True
        thread.start()

        # 메인 스레드는 사용자 입력을 기다림
        print("객체 감지 결과 모니터링 중... (종료하려면 Ctrl+C)")
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break

    finally:
        # 파이프라인 정리
        loop.quit()
        pipeline.set_state(Gst.State.NULL)
        print("파이프라인이 종료되었습니다.")


def run_all_commands():
    # 환경 변수 설정 - 한 번만 설정
    os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
    os.environ["WAYLAND_DISPLAY"] = "wayland-1"

    # GStreamer 파이프라인 직접 실행
    run_gstreamer_pipeline()


# 모든 명령어 실행
if __name__ == "__main__":
    run_all_commands()
