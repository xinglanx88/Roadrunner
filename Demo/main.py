# main.py
import cv2
# from PyQt5.QtWidgets import QApplication
# from gui import DemoWindow  # Import your GUI class
import detection_fast  # Import your YOLO pipeline
import shared  # Import shared variables

def main():
    # Start the YOLO pipeline in a background thread
    pipeline = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw, width=1280, height=720, format=BGRx ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! "
    "appsink drop=true"
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

    shared.vidgoing = False
    read.join()
    process.join()
    cap.release()

if __name__ == "__main__":
    main()
