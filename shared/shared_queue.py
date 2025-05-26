import queue

detectionQueue = queue.Queue(maxsize=5)  # 감지 결과 큐
shotFlagQueue = queue.Queue(maxsize=5)  # 스냅샷 신호 큐
metaQueue = queue.Queue(maxsize=5)  # 메타데이터 큐
