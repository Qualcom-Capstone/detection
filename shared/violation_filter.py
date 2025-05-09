import time

recent_violation = {}  # 과속한 차량들 cache
VIOLATION_COOLTIME = 3  # 위반 쿨타임은 3초임


def should_send_violation(obj_id):
    now = time.time()
    last_time = recent_violation.get(obj_id)

    if last_time is None or (now - last_time) > VIOLATION_COOLTIME:  # 쿨타임보다 오래된거거나 새로 등장한 차량이면
        recent_violation[obj_id] = now  # 캐시에 넣음
        return True
    else:
        return False
