# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui import DemoWindow  # Import your GUI class
import yolo_pipeline  # Import your YOLO pipeline
import shared  # Import shared variables

def main():
    # Start the YOLO pipeline in a background thread
    yolo_thread = yolo_pipeline.start_yolo()

    # Start the PyQt5 GUI
    app = QApplication(sys.argv)
    demo_window = DemoWindow()
    demo_window.show()

    # Run the Qt event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
