"""
IOU 계산한다.
두개의 바운딩박스를 받고,
겹치는 면적을 비교함
"""


def compute_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # 우측 하단 점 좌표
    x1_max, y1_max = x1 + w1, y1 + h1
    x2_max, y2_max = x2 + w2, y2 + h2

    # 교차 영역 좌상단/우하단 좌표 계산
    inter_x_min = max(x1, x2)
    inter_y_min = max(y1, y2)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    # 겹치는 면적 구함
    inter_area = max(0, inter_x_max - inter_x_min) * max(0, inter_y_max - inter_y_min)

    area1 = w1 * h1  # 첫번째 프레임 면적
    area2 = w2 * h2  # 두번째 프레임 면적
    union_area = area1 + area2 - inter_area  # 두 면적의 합집합을 구함

    return inter_area / union_area if union_area > 0 else 0  # IoU반환


def is_iou_match(detected, tracked_objects, iou_threshold):
    for tracked in tracked_objects:
        iou_val = compute_iou((detected.coord.x, detected.coord.y, detected.coord.w, detected.coord.h),
                              (tracked.coord.x, tracked.coord.y, tracked.coord.w, tracked.coord.h))

        if iou_val > iou_threshold:
            return tracked.id
    return None
