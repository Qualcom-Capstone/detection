import subprocess
import os

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


def run_all_commands():
    # 환경 변수 설정
    os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
    os.environ["WAYLAND_DISPLAY"] = "wayland-1"

    # 실행할 명령어 리스트
    commands = [
        "export XDG_RUNTIME_DIR=/dev/socket/weston",
        "export WAYLAND_DISPLAY=wayland-1",
        "setprop persist.overlay.use_c2d_blit 2",
        "gst-launch-1.0 -e --gst-debug=1 qtiqmmfsrc name=camsrc camera=0 ! video/x-raw\\(memory:GBM\\),format=NV12,width=1280,height=720,framerate=30/1,compression=ubwc ! queue ! tee name=split split. ! queue ! qtivcomposer name=mixer sink_1::dimensions=\"<1920,1080>\" ! queue ! waylandsink fullscreen=true sync=true split. ! queue ! qtimlvconverter ! queue ! qtimlsnpe delegate=dsp model=/opt/yolonas.dlc layers=\"</heads/Mul, /heads/Sigmoid>\" ! queue ! qtimlvdetection threshold=51.0 results=10 module=yolo-nas labels=/opt/yolonas.labels ! video/x-raw,width=640,height=360 ! queue ! mixer."
    ]

    # 명령어 실행
    for command in commands:
        success = run_command(command)
        if not success:
            print(f"Command failed: {command}")
            break
    else:
        print("All commands executed successfully.")

# 모든 명령어 실행
run_all_commands()
