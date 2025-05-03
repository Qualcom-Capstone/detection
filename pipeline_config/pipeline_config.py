# 전체 영상에 대해 상하 반전을 inference + display 양쪽에 모두 적용하기 위해
# tee 이전에 qtivtransform flip-vertical=true 삽입
# threshold에 따라서 프레임 드랍 현상 생김 -> 조정 필요

pipeline_str = (
    'qtiqmmfsrc camera=0 ! '
    'qtivtransform flip-vertical=true ! '
    'video/x-raw(memory:GBM),format=NV12,width=1920,height=1080,framerate=30/1 ! '
    'tee name=t '
    't. ! queue ! qtimetamux name=mux ! qtioverlay ! waylandsink fullscreen=true sync=false '
    't. ! queue ! qtimlvconverter ! '
    'qtimlsnpe delegate=dsp model=/opt/yolonas.dlc layers="</heads/Mul,/heads/Sigmoid>" ! '
    'qtimlvdetection module=yolo-nas labels=/opt/yolonas.labels threshold=71.0 results=10 ! '
    'text/x-raw ! tee name=mt '
    'mt. ! queue ! mux. '
    'mt. ! queue ! appsink name=meta_sink emit-signals=true sync=false drop=true max-buffers=1 '
    't. ! queue ! qtivtransform ! videoconvert ! '
    'video/x-raw,format=RGB,width=1920,height=1080 ! '
    'appsink name=frame_sink emit-signals=false sync=false max-buffers=1 drop=true'
)


def get_pipeline():
    return pipeline_str
