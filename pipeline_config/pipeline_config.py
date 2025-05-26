# 전체 영상에 대해 상하 반전을 inference + display 양쪽에 모두 적용하기 위해
# tee 이전에 qtivtransform flip-vertical=true 삽입
# threshold에 따라서 프레임 드랍 현상 생김 -> 조정 필요

pipeline_str = (
    'qtiqmmfsrc name=camsrc camera=0 ! '
    'qtivtransform flip-vertical=true ! '
    'video/x-raw(memory:GBM),format=NV12,width=1920,height=1080,framerate=20/1 ! '
    'queue ! tee name=split '
    'split. ! queue ! '
    'qtimetamux name=metamux ! queue ! '
    'qtioverlay ! queue ! '
    'waylandsink sync=false fullscreen=true '
    'split. ! queue ! qtimlvconverter ! queue ! '
    'qtimltflite delegate=external external-delegate-path=libQnnTFLiteDelegate.so '
    'external-delegate-options="QNNExternalDelegate,backend_type=htp;" '
    'model=/opt/yolov5m-320x320-int8.tflite ! queue ! '
    'qtimlvdetection threshold=71.0 results=10 module=yolov5 '
    'labels=/opt/yolov5m.labels '
    'constants="YoloV5,q-offsets=<3.0>,q-scales=<0.005047998391091824>;" ! '
    'text/x-raw ! tee name=mt '
    'mt. ! queue ! metamux. '
    'mt. ! queue ! appsink name=meta_sink emit-signals=true sync=false drop=true max-buffers=1 '
    'split. ! queue ! qtivtransform ! videoconvert ! '
    'video/x-raw,format=RGB,width=1920,height=1080 ! '
    'appsink name=frame_sink emit-signals=false sync=false max-buffers=1 drop=true'
)


def get_pipeline():
    return pipeline_str
