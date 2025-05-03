from gi.repository import Gst


def save_raw_frame_as_jpeg(frame_bytes, filename):
    Gst.init(None)

    pipeline_str = (
            "appsrc name=mysrc is-live=true block=true format=3 ! "
            "videoconvert ! jpegenc ! filesink location=" + filename
    )

    pipeline = Gst.parse_launch(pipeline_str)
    appsrc = pipeline.get_by_name("mysrc")
    safe_caps = "video/x-raw, format=RGB, width=1920, height=1080"
    caps = Gst.Caps.from_string(safe_caps)
    appsrc.set_property("caps", caps)

    pipeline.set_state(Gst.State.PLAYING)

    buf = Gst.Buffer.new_allocate(None, len(frame_bytes), None)
    buf.fill(0, frame_bytes)
    appsrc.emit("push-buffer", buf)
    appsrc.emit("end-of-stream")

    bus = pipeline.get_bus()
    bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.EOS)
    pipeline.set_state(Gst.State.NULL)
