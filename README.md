# Rubik Pi Object Detection

실시간 과속 차량 감지 시스템 on **Rubik Pi**

A real-time speeding vehicle detection system on **Rubik Pi**

# Overview

이 프로젝트는 Qualcomm 기반 Rubik Pi 하드웨어에서 YOLO 객체 탐지와 GStreamer를 활용해, 실시간으로 과속 차량을 감지하는 완전한 엣지 기반 시스템입니다.
카메라 입력부터 추론, 트래킹, 속도 측정, 과속 차량 촬영까지 모든 과정을 로컬에서 처리하므로 클라우드 연산이 전혀 필요하지 않습니다.

This project is a fully edge-based system that detects speeding vehicles in real time using YOLO object detection +
GStreamer on Qualcomm-based Rubik Pi hardware. It avoids the need for cloud computation by processing everything
locally — from camera input to inference, tracking, speed calculation, and violation capture.

# Tech Stack

| Category             | Technologies                                                    |
|----------------------|-----------------------------------------------------------------|
| **Hardware**         | Rubik Pi 3, IMX477 image sensor, 10MP HQ Lens(16mm)             |
| **Object Detection** | YOLOv5m                                                         |
| **Acceleration**     | Qualcomm SNPE + TFLite delegate                                 |
| **Pipeline**         | GStreamer                                                       |
| **Programming**      | Python                                                          |
| **Features**         | On-device tracking, speed measurement, snapshot, multithreading |

# Table of Contents

+ 실행 방법 How to Run
+ 파이프라인 구성 GStreamer + YOLO Pipeline
+ 객체 트래킹 Object Tracking
+ 속도 측정 Speed Measurement
+ 멀티 스레딩 Multithreading

## How to Run

root 디렉토리 밑에 run.sh를 실행한다.

Execute the run.sh script from the root directory.

```plain
/run.sh 소스

export PYTHONPATH=$(pwd)
python main.py 2>/dev/null
```

`./run.sh`로 실행.

내부 디버깅 출력문을 전부, 생략한다(터미널 IO최소화)

Run with `./run.sh.`

All internal debug print statements are suppressed to minimize terminal I/O.

---

## GStremaer, YOLO pipeline

```plain
qtiqmmfsrc (camera=0)
└── qtivtransform (flip-vertical=true)
    └── video/x-raw (NV12, 1920x1080, GBM)
        └── queue
            └── tee name=split
                ├── [Display Branch]
                │   └── queue
                │       └── qtimetamux name=metamux
                │           └── queue
                │               └── qtioverlay
                │                   └── waylandsink (fullscreen=true)
                │
                ├── [Inference Branch]
                │   └── queue
                │       └── qtimlvconverter
                │           └── queue
                │               └── qtimltflite (delegate=external, model=yolov5m)
                │                   └── queue
                │                       └── qtimlvdetection (threshold=71.0)
                │                           └── text/x-raw
                │                               └── tee name=mt
                │                                   ├── queue → metamux
                │                                   └── queue → appsink name=meta_sink (emit-signals=true)
                │
                └── [Frame Capture Branch]
                    └── queue
                        └── qtivtransform
                            └── videoconvert
                                └── video/x-raw (RGB)
                                    └── appsink name=frame_sink

```

---

## Object Tracking (IoU)

<img src="https://github.com/user-attachments/assets/868437d2-78e2-4d52-89a7-3d7f9e850517" width="300" height="200">

IoU를 계산하여, 다음프레임의 객체가 같은 객체인지 판단한다.

## Speed Measurement

### Method 1 (Not Used)

<img src="https://github.com/user-attachments/assets/9980f43f-7990-47aa-a222-8e350e34666c" width="300" height="200">

프레임간 중심 좌표의 이동거리 변화로 속도를 측정

Speed is calculated based on the change in the object's center coordinates across frames.

### Method 2 (✅Selected)

<img src="https://github.com/user-attachments/assets/e6d91e45-a950-47ad-8ef3-96aa008875cb" width="300" height="200">

가상의 두 선을 그어놓고, 두 선을 동과하는데 걸리는 시간을 측정한다.

하지만, 이 방법은 가상의 두 선 사이의 실제 도로 거리를 알아야 정확히 측정 할 수 있다.

Two virtual lines are drawn on the screen,

and the time taken for the object to pass between these lines is measured.

However, to calculate the speed accurately, the real-world distance between the two lines must be known.

## Multi Threading

병목 현상을 최소화 하기 위해서 멀티 스레딩을 사용했다.

Multithreading is used to minimize bottlenecks and enhance performance.

<img src="https://github.com/user-attachments/assets/c24c68ef-23f3-4e48-8641-be3eba475cd7" width="900" height="200">

+ 메인 스레드 Main Thread
+ 트래킹, 속도 측정 스레드 Tracking & Speed Measurement Thread
+ 사진촬영 및 전송 스레드 Screenshot & Upload Thread

