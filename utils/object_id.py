"""
이 파일은 감지된 객체에 대한 특정 id를 부여하는 파일임
"""
global_id = 0


def assign_id():
    global global_id
    id_to_assign = global_id
    global_id += 1
    return id_to_assign