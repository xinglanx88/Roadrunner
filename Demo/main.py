# main.py
import cv2
from PyQt5.QtWidgets import QApplication
# from gui import DemoWindow  # Import your GUI class
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
    "video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw,format=BGRx ! "
    "videoconvert ! "
    "video/x-raw,format=BGR ! "
    "appsink drop=true sync=false max-buffers=1"
)

    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)


    read, process = detection_fast.startYolo(cap)
    read.start()
    process.start()

    # app = QApplication(sys.argv)
    # demo_window = DemoWindow()
    # demo_window.show()

    # Run the Qt event loop
    # sys.exit(app.exec_())

    shared.vidgoing = True
    read.join()
    process.join()
    cap.release()


def main_2():
    # 1. Build the GStreamer pipeline string (your 1920×1080/30 fps setup)
    pipeline = (
      "nvarguscamerasrc sensor-id=0 ! "
      "video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1 ! "
      "nvvidconv flip-method=0 ! "
      "video/x-raw,format=BGRx ! "
      "videoconvert ! "
      "video/x-raw,format=BGR ! "
      "appsink drop=true sync=false max-buffers=1"
    )
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

    # 2. Make sure we actually want to keep reading
    shared.vidgoing = True

    # 3. Launch your consume/produce threads
    read_thread, process_thread = detection_fast.startYolo(cap)
    read_thread.daemon = True
    process_thread.daemon = True
    read_thread.start()
    process_thread.start()

    # 4. Block here until user hits Ctrl-C
    try:
        while shared.vidgoing:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping...")
        shared.vidgoing = False

    # 5. Clean up
    read_thread.join()
    process_thread.join()
    cap.release()
    print("Exited cleanly.")

if __name__ == "__main__":
    main_2()
