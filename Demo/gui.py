# gui.py
import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
import shared  # Import shared variables

class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO License Plate Demo")

        # Image display
        self.image_label = QLabel()

        # Plate label
        self.plate_label = QLabel("Detected Plate: N/A")
        self.plate_label.setAlignment(Qt.AlignCenter)
        self.plate_label.setFixedHeight(40)
        self.plate_label.setStyleSheet("font-size: 24px;")

        # Back button
        self.back_button = QPushButton("Back to Menu")
        self.back_button.setFixedHeight(40)
        self.back_button.clicked.connect(self.back_to_menu)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.plate_label)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        # Timer for periodic frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # approx ~30 FPS

    def update_frame(self):
        if shared.latest is not None:
            frame = shared.latest.copy()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qimg))

            # Update plate label
            self.plate_label.setText(f"Detected Plate: {shared.last_plate}")

    def back_to_menu(self):
        shared.vidgoing = False  # Stop the YOLO pipeline thread
        self.timer.stop()
        self.close()  # Or emit a signal to go back to a stacked menu view
