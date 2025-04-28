# main.py
import sys
sys.path.append('/usr/lib/python3.10/dist-packages')

import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from gui import DemoWindow  # Import your GUI class
from Display import MainWindow
import detection_fast  # Import your YOLO pipeline
import shared  # Import shared variables
import time
def main():
    # Start the YOLO pipeline in a background thread
    """
    pipeline = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw, width=1280, height=720, format=BGRx ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! "
    "appsink drop=true"
)"""
    pipeline = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM), width=1920, height=1080, framerate=60/1 ! "
    "nvvidconv ! "
    "video/x-raw, format=BGRx ! "  # Convert to BGRx (RGB-like format)
    "appsink"
)

    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)


    read, process = detection_fast.startYolo(cap)
    read.start()
    process.start()

    app = QApplication(sys.argv)
    demo_window = DemoWindow()
    demo_window.show()

    #Run the Qt event loop
    sys.exit(app.exec_())

    shared.vidgoing = True
    read.join()
    process.join()
    cap.release()
def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920, capture_height=1080,
    display_width=1920, display_height=1080,
    framerate=30, flip_method=0):
    return (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        f"video/x-raw(memory:NVMM),width=(int){capture_width},height=(int){capture_height},"
        f"format=(string)NV12,framerate=(fraction){framerate}/1 ! "
        f"nvvidconv flip-method={flip_method} ! "
        f"video/x-raw,format=(string)BGRx ! "
        f"videoconvert ! "
        f"video/x-raw,format=(string)BGR ! "
        "appsink drop=true sync=false max-buffers=1"
    )


def main_2():
    # 1. Build the GStreamer pipeline string (your 1920×1080/30 fps setup)
    """
    pipeline = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw,format=BGRx ! "
    "videoconvert ! "
    "video/x-raw,format=BGR ! "
    "appsink drop=true sync=false max-buffers=1"
)"""
    pipeline = gstreamer_pipeline(0,1920,1080,1920,1080,30,0)
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

    # 2. Make sure we actually want to keep reading
    shared.vidgoing = True

    # 3. Launch your consume/produce threads
    read_thread, process_thread = detection_fast.startYolo(cap)
    read_thread.daemon = True
    process_thread.daemon = True
    read_thread.start()
    process_thread.start()

    # Handle Ctrl-C gracefully

    # Start Qt app
    app = QApplication(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    app.exec_()

    # Clean up after Qt loop exits
    shared.vidgoing = False
    read_thread.join()
    process_thread.join()
    cap.release()
    print("Exited cleanly.")

if __name__ == "__main__":
    main_2()
