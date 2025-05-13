import queue

detectionQueue = queue.Queue(maxsize=5)  # 감지 결과 큐
imageQueue = queue.Queue(maxsize=5)  # 이미지 큐
metaQueue = queue.Queue(maxsize=5)  # 메타데이터 큐
