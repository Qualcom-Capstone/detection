# Rubik Pi Object Detection

실시간 과속 차량 감지 시스템 on **Rubik Pi**

# 목차
+ 실행 방법
+ 파이프라인 구성
+ 객체 트래킹
+ 속도 측정
+ 멀티 스레딩

## 실행

root 디렉토리 밑에 run.sh를 실행한다.

```plain
/run.sh 소스

export PYTHONPATH=$(pwd)
python main.py 2>/dev/null
```

`./run.sh`로 실행.

내부 디버깅 출력문을 전부, 생략한다(터미널 IO최소화)

---

## GStremaer, YOLO 파이프라인 구성

```plain
qtiqmmfsrc (카메라 입력)
    → qtivtransform (flip-vertical 적용)
    → tee split
        ├── qtimetamux → qtioverlay → waylandsink (화면 출력)
        ├── qtimlvconverter → qtimltflite → qtimlvdetection
                → tee mt
                    ├── metamux (메타데이터 합성용)
                    └── appsink meta_sink (메타데이터 수신, emit-signals=true)
        └── qtivtransform → videoconvert → appsink frame_sink (프레임 캡처용)
```

---

## 객체 트래킹 (IoU)


## Speed Calculate
