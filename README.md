# Rubik Pi Object Detection

실시간 과속 차량 감지 시스템 on **Rubik Pi**

# Table of Contents

+ 실행 방법 How to Run
+ 파이프라인 구성 GStreamer + YOLO Pipeline
+ 객체 트래킹 Object Tracking
+ 속도 측정 Speed Measurement
+ 멀티 스레딩 Multithreading

## How to Run

root 디렉토리 밑에 run.sh를 실행한다.

```plain
/run.sh 소스

export PYTHONPATH=$(pwd)
python main.py 2>/dev/null
```

`./run.sh`로 실행.

내부 디버깅 출력문을 전부, 생략한다(터미널 IO최소화)

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

<img src="https://github.com/user-attachments/assets/dba955f8-c974-41ce-9d1e-6f675a636b09" width="300" height="200">

프레임간 중심 좌표의 이동거리 변화로 속도를 측정

Speed is calculated based on the change in the object's center coordinates across frames.

### Method 2 (Selected)
<img src="https://github.com/user-attachments/assets/e6d91e45-a950-47ad-8ef3-96aa008875cb" width="300" height="200">

가상의 두 선을 그어놓고, 두 선을 동과하는데 걸리는 시간을 측정한다.

하지만, 이 방법은 가상의 두 선 사이의 실제 도로 거리를 알아야 정확히 측정 할 수 있다.

Two virtual lines are drawn on the screen,

and the time taken for the object to pass between these lines is measured.

However, to calculate the speed accurately, the real-world distance between the two lines must be known.

---

## Multi Threading

병목 현상을 최소화 하기 위해서 멀티 스레딩을 사용했다.

Multithreading is used to minimize bottlenecks and enhance performance.

+ 메인 스레드 Main Thread
+ 트래킹, 속도 측정 스레드 Tracking & Speed Measurement Thread
+ 사진촬영 및 전송 스레드 Screenshot & Upload Thread

