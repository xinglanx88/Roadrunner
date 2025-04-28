# gui.py
import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
import shared  # Import shared variables

import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('License Plate Detection')
        self.setGeometry(100, 100, 1920, 1080)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Back button
        self.back_button = QPushButton("Back to Menu", self)
        self.back_button.setFixedHeight(40)
        self.back_button.clicked.connect(self.back_to_menu)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.back_button)
        self.setLayout(layout)


        # Timer for periodic frame updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # approx ~30 FPS

    def update_frame(self):
        # Ensure shared.plate_frame has valid data (non-None)
        if hasattr(shared, 'plate_frame') and shared.plate_frame is not None:
            frame = shared.plate_frame.copy()

            if frame.shape[2] == 3:
                # No need to convert, just change from BGR to RGB for display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                print("Error: Unexpected number of channels in the frame!")

            # Convert the frame to QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(q_img))
        else:
            print("tf")

        
    def back_to_menu(self):
        shared.vidgoing = False  # Stop the YOLO pipeline thread
        self.timer.stop()
        self.close()  # Or emit a signal to go back to a stacked menu view