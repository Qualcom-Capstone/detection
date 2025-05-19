import gi, os

gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GLib
import cairo

Gst.init(None)

os.environ["XDG_RUNTIME_DIR"] = "/dev/socket/weston"
os.environ["WAYLAND_DISPLAY"] = "wayland-1"

def draw_overlay(overlay, context, timestamp, duration):
    width, height = 1920, 1080
    y1, y2 = 500, 900

    context.set_line_width(3)

    # 빨간 선
    context.set_source_rgba(1, 0, 0, 0.8)
    context.move_to(0, y1)
    context.line_to(width, y1)
    context.stroke()

    # 초록 선
    context.set_source_rgba(0, 1, 0, 0.8)
    context.move_to(0, y2)
    context.line_to(width, y2)
    context.stroke()


pipeline_str = (
    'qtiqmmfsrc camera=0 ! '
    'qtivtransform flip-vertical=true ! '
    'video/x-raw, width=1920, height=1080, framerate=15/1 ! '
    'videoscale ! videoconvert ! '
    'cairooverlay name=line_overlay ! '
    'videoconvert ! '
    'video/x-raw, width=1920, height=1080 ! '
    'waylandsink fullscreen=true sync=false'
)

pipeline = Gst.parse_launch(pipeline_str)
overlay = pipeline.get_by_name("line_overlay")
overlay.connect("draw", draw_overlay)

pipeline.set_state(Gst.State.PLAYING)
loop = GLib.MainLoop()

try:
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    pipeline.set_state(Gst.State.NULL)