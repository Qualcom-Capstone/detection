# detection
Rubik-Pi object detection

## 목표
+ Yolo모델, Rubik3보드 환경 구축
+ GStreamer 그 외의 plug-in 들의 이해
+ 객체 탐지, bounding box, label 등 화면 출력
+ ㅡㅡㅡㅡㅡㅡㅡㅡㅡ여기까지 블로그에 후기 올림ㅡㅡㅡㅡㅡㅡㅡㅡㅡ
+ 객체 트래킹
+ 객체 속도 측정
+ OCR
+ 과속 시, API call, 서버 전송
---

## 실행
루트경로는 `detection` 디렉토리로 생각한다.
원래 루트 경로는 `rubik-detection` 인데, `main.py`가
detection디렉토리 밑에 있기 때문에, 루트는 detection으로 정한다.

따라서 `./run_detection.sh`를 실행할 때도 실행의 위치가
detection 디렉토여야 한다.

`chmod +x run_detection.sh`를 하여 .sh에 실행권한 부여

`./run_detection.sh`를 입력하여 실행
