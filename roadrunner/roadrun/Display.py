import sys
import cv2
from PyQt5.QtWidgets import (
    QApplication, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QStackedWidget, QLineEdit
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt



class MainMenu(QWidget):
    """Main menu with navigation buttons."""
    def __init__(self, stacked_widget, app):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Main Menu")

        layout_main = QVBoxLayout()

        layout_label = QHBoxLayout()
        label = QLabel("📋 Main Menu", self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(10)
        layout_label.addWidget(label)

        layout_main.addLayout(layout_label)
        

        grid_layout = QGridLayout()
        # Navigation Buttons
        btn_camera = QPushButton("📷 Open Camera Feed")
        btn_camera.clicked.connect(self.switch_to_camera)

        btn_input = QPushButton("⌨️ Input License Plate")
        btn_input.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        btn_current = QPushButton("🚗 View Current Identifications")
        btn_current.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        btn_history = QPushButton("📜 View License Plate History")
        btn_history.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))

        btn_temp = QPushButton("Temp Button")

        btn_exit = QPushButton("❌ Exit")
        btn_exit.clicked.connect(app.quit)

        grid_layout.addWidget(btn_camera, 0, 0)
        grid_layout.addWidget(btn_input, 0, 1)
        grid_layout.addWidget(btn_current, 0, 2)
        grid_layout.addWidget(btn_history, 1, 0)
        grid_layout.addWidget(btn_temp, 1, 1)
        grid_layout.addWidget(btn_exit, 1, 2)

        layout_main.addLayout(grid_layout)

        self.setLayout(layout_main)

    def switch_to_camera(self):
        """Start the camera and switch to the camera feed screen."""
        self.stacked_widget.camera_screen.start_camera()
        self.stacked_widget.setCurrentIndex(1)


class CameraFeed(QWidget):
    """Displays the camera feed."""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Live Camera Feed")

        self.video_label = QLabel(self)
        self.back_button = QPushButton("🔙 Back to Menu")
        self.back_button.clicked.connect(self.return_to_menu)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def start_camera(self):
        """Start the camera when the screen is shown."""
        if not self.cap.isOpened():
            self.cap.open(0)
        self.timer.start(30)

    def update_frame(self):
        """Fetch a new frame from the camera and display it."""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def return_to_menu(self):
        """Stop camera and return to the main menu."""
        self.timer.stop()
        self.cap.release()
        self.video_label.clear()
        self.stacked_widget.setCurrentIndex(0)  # Go back to the main menu


class LicensePlateInput(QWidget):
    """License Plate Input Screen."""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("License Plate Input")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter License Plate:"))
        self.plate_input = QLineEdit()
        layout.addWidget(self.plate_input)

        self.submit_button = QPushButton("✅ Submit")
        self.submit_button.clicked.connect(self.submit_plate)
        layout.addWidget(self.submit_button)

        self.back_button = QPushButton("🔙 Back to Menu")
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def submit_plate(self):
        """Handle license plate submission (placeholder functionality)."""
        plate = self.plate_input.text()
        print(f"License plate submitted: {plate}")  # Placeholder for future database storage
        self.plate_input.clear()


class CurrentIdentifications(QWidget):
    """Displays currently identified license plates."""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Current Identifications")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("🚗 Currently Identified Plates:"))

        self.current_list = QLabel("No plates identified yet.")  # Placeholder for real-time updates
        layout.addWidget(self.current_list)

        self.back_button = QPushButton("🔙 Back to Menu")
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(self.back_button)

        self.setLayout(layout)


class PlateHistory(QWidget):
    """Displays the history of identified license plates."""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("License Plate History")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("📜 License Plate History:"))

        self.history_list = QLabel("No history available.")  # Placeholder for data storage
        layout.addWidget(self.history_list)

        self.back_button = QPushButton("🔙 Back to Menu")
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(self.back_button)

        self.setLayout(layout)


class MainWindow(QStackedWidget):
    """Main window managing all screens."""
    def __init__(self, app):
        super().__init__()

        self.camera_screen = CameraFeed(self)
        self.menu_screen = MainMenu(self, app)
        self.plate_input_screen = LicensePlateInput(self)
        self.current_id_screen = CurrentIdentifications(self)
        self.history_screen = PlateHistory(self)

        self.addWidget(self.menu_screen)  # Index 0
        self.addWidget(self.camera_screen)  # Index 1
        self.addWidget(self.plate_input_screen)  # Index 2
        self.addWidget(self.current_id_screen)  # Index 3
        self.addWidget(self.history_screen)  # Index 4

        self.setCurrentIndex(0)  # Start on the main menu

        self.showFullScreen()




# Run the PyQt app
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
