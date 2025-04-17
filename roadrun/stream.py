import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

# Initialize GStreamer
Gst.init(None)

def create_pipeline(width, height, framerate):
    # Create the elements for the pipeline
    pipeline = Gst.Pipeline.new("camera-pipeline")

    # Create the camera source element
    nvarguscamerasrc = Gst.ElementFactory.make("nvarguscamerasrc", "camera-source")
    if not nvarguscamerasrc:
        print("Error: Could not create 'nvarguscamerasrc'")
        return None
    
    # Set properties for the camera source
    nvarguscamerasrc.set_property("sensor-id", 0)  # 0 for CAM0

    # Create a converter element to handle format conversion
    bayer2rgb = Gst.ElementFactory.make("bayer2rgb", "bayer-to-rgb")
    if not bayer2rgb:
        print("Error: Could not create 'bayer2rgb'")
        return None

    # Create a video sink for displaying the output
    nveglglessink = Gst.ElementFactory.make("nveglglessink", "video-sink")
    if not nveglglessink:
        print("Error: Could not create 'nveglglessink'")
        return None

    # Set the caps (format, width, height, framerate)
    caps = Gst.Caps.from_string(f"video/x-raw(memory:NVMM), width={width}, height={height}, framerate={framerate}/1, format=NV12")
    
    # Link the elements together
    pipeline.add(nvarguscamerasrc)
    pipeline.add(bayer2rgb)
    pipeline.add(nveglglessink)
    
    nvarguscamerasrc.link(bayer2rgb)
    bayer2rgb.link_filtered(nveglglessink, caps)

    return pipeline

def main():
    # Get the width, height, and framerate from the user or set default values
    width = int(input("Enter width (e.g., 1920): ") or 1920)
    height = int(input("Enter height (e.g., 1080): ") or 1080)
    framerate = int(input("Enter framerate (e.g., 30): ") or 30)

    # Create the pipeline
    pipeline = create_pipeline(width, height, framerate)

    if pipeline is None:
        print("Failed to create pipeline.")
        sys.exit(1)

    # Start playing the pipeline
    pipeline.set_state(Gst.State.PLAYING)
    print("Pipeline is now playing. Press Ctrl+C to stop.")

    # Start the GStreamer main loop
    loop = GObject.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)
        print("Pipeline stopped.")

if __name__ == "__main__":
    main()
