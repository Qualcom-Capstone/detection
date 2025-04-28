"""
메타데이터 파싱 관련한 함수들 모아 놓은 파일
"""
import re



# 메타데이터 파싱 함수
def parse_metadata(txt):
    cleaned = txt.encode('utf-8').decode('unicode_escape')
    cleaned = cleaned.replace('\\', '')
    m = re.search(r'bounding-boxes=\(structure\)<(.*?)>,\s*timestamp', cleaned, re.DOTALL)
    if not m:
        return

    content = m.group(1)
    entries = re.findall(r'"(.*?)"', content)

    for obj in entries:
        label_match = re.match(r'([a-zA-Z0-9_.]+)', obj)
        label = label_match.group(1) if label_match else "unknown"

        # 바운딩 박스 추출
        rect_match = re.search(
            r'rectangle=\(float\)<\s*([\d\.\-e]+)\s*,\s*([\d\.\-e]+)\s*,\s*([\d\.\-e]+)\s*,\s*([\d\.\-e]+)\s*>', obj)
        if rect_match:
            x, y, w, h = map(float, rect_match.groups())
            print(f"[DETECTED] label: {label}, bbox: x={x:.3f}, y={y:.3f}, w={w:.3f}, h={h:.3f}")
        else:
            print(f"[DETECTED] label: {label}, but no rectangle found")
