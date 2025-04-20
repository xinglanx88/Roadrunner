import sys
import cv2
from PyQt5.QtWidgets import (
    QApplication, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QStackedWidget, QLineEdit, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt, QEvent



class MainMenu(QWidget):
    """Main menu with navigation buttons."""
    def __init__(self, stacked_widget, app):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Main Menu")

        layout_main = QVBoxLayout()

        label = QLabel("📋 Main Menu", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 48px;")
        label.setFixedHeight(80)

        layout_main.addWidget(label)
        

        grid_layout = QGridLayout()
        # Navigation Buttons
        btn_camera = QPushButton("📷 Open Camera\nFeed")
        btn_camera.clicked.connect(self.switch_to_camera)

        btn_input = QPushButton("⌨️ Input License\nPlate")
        btn_input.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        btn_current = QPushButton("🚗 View Ongoing\nIdentifications")
        btn_current.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        btn_history = QPushButton("📜 View License\nPlate History")
        btn_history.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))

        btn_temp = QPushButton("📜 View License\nPlate Inputs")
        btn_temp.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))

        btn_exit = QPushButton("❌ Exit")
        btn_exit.clicked.connect(app.quit)

        buttons = [btn_camera, btn_input, btn_current, btn_history, btn_temp, btn_exit]

        grid_layout.addWidget(btn_camera, 0, 0)
        grid_layout.addWidget(btn_input, 0, 1)
        grid_layout.addWidget(btn_current, 0, 2)
        grid_layout.addWidget(btn_history, 1, 0)
        grid_layout.addWidget(btn_temp, 1, 1)
        grid_layout.addWidget(btn_exit, 1, 2)

        for btn in buttons:
            btn.setFixedHeight(180)
            btn.setStyleSheet("font-size: 24px;")


        layout_main.addLayout(grid_layout)

        self.setLayout(layout_main)

    def switch_to_camera(self):
        """Start the camera and switch to the camera feed screen."""
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

        import cv2

        # Define the GStreamer pipeline
        self.gstreamer_pipeline = (
            "v4l2src device=/dev/video1 ! "
            "video/x-raw, format=YUY2, width=640, height=480, framerate=30/1 ! "
            "videoconvert ! "
            "appsink"
        )

        # Create a VideoCapture object using the GStreamer pipeline
        self.cap = cv2.VideoCapture("/dev/video0")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def showEvent(self, event: QEvent):
        super().showEvent(event)
        self.start_camera()

    def start_camera(self):
        """Start the camera when the screen is shown."""
        if not self.cap.isOpened():
            print("kill yourself")
            self.cap.open(self.gstreamer_pipeline, cv2.CAP_GSTREAMER)
        self.timer.start(30)

    def update_frame(self):
        """Fetch a new frame from the camera and display it."""
        ret, frame = self.cap.read()
        if ret:
            print(f"Original frame shape: {frame.shape}")  # Check frame shape

            # If the frame already has 3 channels (BGR or other formats), we skip the YUYV to BGR conversion
            if frame.shape[2] == 3:
                # No need to convert, just change from BGR to RGB for display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                print("Error: Unexpected number of channels in the frame!")

            # Convert the frame to QImage
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

    """Displays the camera feed."""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Demo Feed")

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 48px;")
        self.label.setFixedHeight(40)

        self.video_label = QLabel(self)

        self.back_button = QPushButton("🔙 Back to Menu")
        self.back_button.clicked.connect(self.return_to_menu)
        self.back_button.setFixedHeight(40)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        import cv2

        # Define the GStreamer pipeline
        self.gstreamer_pipeline = (
            "v4l2src device=/dev/video1 ! "
            "video/x-raw, format=YUY2, width=640, height=480, framerate=30/1 ! "
            "videoconvert ! "
            "appsink"
        )

        # Create a VideoCapture object using the GStreamer pipeline
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def showEvent(self, event: QEvent):
        super().showEvent(event)
        self.start_camera()

    def start_camera(self):
        """Start the camera when the screen is shown."""
        if not self.cap.isOpened():
            print("kill yourself")
            self.cap.open(self.gstreamer_pipeline, cv2.CAP_GSTREAMER)
        self.timer.start(30)

    def update_frame(self):
        """Fetch a new frame from the camera and display it."""
        ret, frame = self.cap.read()
        if ret:
            print(f"Original frame shape: {frame.shape}")  # Check frame shape

            # If the frame already has 3 channels (BGR or other formats), we skip the YUYV to BGR conversion
            if frame.shape[2] == 3:
                # No need to convert, just change from BGR to RGB for display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                print("Error: Unexpected number of channels in the frame!")

            # Convert the frame to QImage
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


class OnScreenKeyboard(QWidget):
    def __init__(self, line_edit):
        super().__init__()
        self.line_edit = line_edit
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        self.setLayout(layout)

        keys = [
            '1','2','3','4','5','6','7','8','9','0',
            'Q','W','E','R','T','Y','U','I','O','P',
            'A','S','D','F','G','H','J','K','L',
            'Z','X','C','V','B','N','M',
            '←','Space','Enter'
        ]

        row, col = 0, 0
        for key in keys:
            button = QPushButton(key)
            button.setFixedSize(60, 60)
            button.setStyleSheet("font-size: 18px;")
            button.clicked.connect(lambda _, k=key: self.key_pressed(k))
            layout.addWidget(button, row, col)
            col += 1
            if key in ['0', 'P', 'L', 'M']:
                row += 1
                col = 0

    def key_pressed(self, key):
        if key == 'Space':
            self.line_edit.insert(' ')
        elif key == '←':
            current_text = self.line_edit.text()
            self.line_edit.setText(current_text[:-1])
        elif key == 'Enter':
            self.parent().submit_plate()
        else:
            self.line_edit.insert(key)


class LicensePlateInput(QWidget):
    """License Plate Input Screen."""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("License Plate Input")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter License Plate:"))
        self.plate_input = QLineEdit()
        self.plate_input.setFixedHeight(60)
        self.plate_input.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.plate_input)

        btn_layout = QHBoxLayout()
        self.submit_button = QPushButton("✅ Submit")
        self.submit_button.setFixedHeight(60)
        self.submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.submit_button.setStyleSheet("font-size: 18px;")
        self.submit_button.clicked.connect(self.submit_plate)

        self.remove_button = QPushButton("Remove Plate")
        self.remove_button.setFixedHeight(60)
        self.remove_button.setStyleSheet("font-size: 18px;")
        self.remove_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.remove_button.clicked.connect(self.remove_plate)

        self.back_button = QPushButton("🔙 Back to Menu")
        self.back_button.setFixedHeight(60)
        self.back_button.setStyleSheet("font-size: 18px;")
        self.back_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        btn_layout.addWidget(self.submit_button)
        btn_layout.addWidget(self.remove_button)
        btn_layout.addWidget(self.back_button)
        layout.addLayout(btn_layout)

        self.keyboard = OnScreenKeyboard(self.plate_input)
        self.keyboard.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.keyboard, stretch=1)


        self.setLayout(layout)


    def submit_plate(self):
        """Handle license plate submission (placeholder functionality)."""
        plate = self.plate_input.text().strip().upper()
        try:
            with open("plates/Plate_Input.txt", "a") as f:
                f.write(plate + "\n")
            print(f"License plate submitted: {plate}")
        except Exception as e:
            print(f"Error writing to file: {e}")

        self.plate_input.clear()
    
    def remove_plate(self):
        target_plate = self.plate_input.text().strip().upper()
        updated_lines = []

        try:
            with open("plates/Plate_Input.txt", "r") as f:
                lines = f.readlines()
                updated_lines = [line for line in lines if line.strip().upper() != target_plate]

            with open("plates/Plate_Input.txt", "w") as f:
                f.writelines(updated_lines)

            print(f"Removed Plate: {target_plate}")
        except FileNotFoundError:
            print("file not found")
        except Exception as e:
            print(f"Error removing plate: {e}")
        
        self.plate_input.clear()


class CurrentIdentifications(QWidget):
    """Displays currently identified license plates."""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Current Identifications")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("📜 Currently Identified Plates:"))

        self.current_list = QLabel("No plates identified yet.")  # Placeholder for real-time updates
        layout.addWidget(self.current_list)

        self.back_button = QPushButton("🔙 Back to Menu")
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(self.back_button)

        self.setLayout(layout)

class CurrentInputs(QWidget):
    """Displays currently identified license plates."""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Current Inputs")

        layout = QVBoxLayout()
        label = QLabel("🚗 Current Plates Being Looked For:")
        label.setFixedHeight(40)
        label.setStyleSheet("font-size: 24px;")
        layout.addWidget(label)


        self.current_list = QLabel("No plates identified yet.")  # Placeholder for real-time updates
        self.current_list.setFixedHeight(300)
        layout.addWidget(self.current_list)

        btn_layout = QHBoxLayout()

        self.back_button = QPushButton("🔙 Back to Menu")
        self.back_button.setFixedHeight(140)
        self.back_button.setStyleSheet("font-size: 48px;")
        self.back_button.clicked.connect(self.go_back)
        btn_layout.addWidget(self.back_button)

        self.remove_all = QPushButton("Remove All")
        self.remove_all.setFixedHeight(140)
        self.remove_all.setStyleSheet("font-size: 48px;")
        self.remove_all.clicked.connect(self.remove_all_plates)
        btn_layout.addWidget(self.remove_all)

        layout.addLayout(btn_layout)
        self.setLayout(layout)


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plate_list)

    def showEvent(self, event: QEvent):
        super().showEvent(event)
        self.timer.start(500)

    def remove_all_plates(self):
        try:
            with open("plates/Plate_Input.txt", "w") as f:
                pass
        except Exception as e:
            print(f"Error reading file: {e}")

    def go_back(self):
        self.timer.stop()
        self.stacked_widget.setCurrentIndex(0)



    def update_plate_list(self):
        plates = []
        try:
            with open("plates/Plate_Input.txt", "r") as f:
                plates = f.readlines()
            plates = [plate.strip() for plate in plates if plate.strip()]


            if plates:
                self.current_list.setText("\n".join(plates))
            else:
                self.current_list.setText("No Plates Input Yet")
            self.adjust_font(plates)

        except Exception as e:
            self.current_list.setText(f"Error reading file: {e}")

    def adjust_font(self, plates):
        num_lines = len(plates) if plates else 1  # Ensure we have at least 1 line

        # Calculate the font size so that the number of lines fits within the fixed height
        font_size = max(10, min(40, 300 // (num_lines * 2)))
        # Apply the font size to the label
        font = QFont("Arial", font_size)
        self.current_list.setFont(font)


class PlateHistory(QWidget):
    """Displays the history of identified license plates."""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("License Plate History")

        layout = QVBoxLayout()
        label = QLabel("📜 License Plate History:")
        label.setFixedHeight(40)
        label.setStyleSheet("fontsize: 24px;")
        layout.addWidget(label)

        self.history_list = QLabel("No history available.")  # Placeholder for data storage
        self.history_list.setFixedHeight(300)
        layout.addWidget(self.history_list)


        btn_layout = QHBoxLayout()

        self.back_button = QPushButton("🔙 Back to Menu")
        self.back_button.setFixedHeight(140)
        self.back_button.setStyleSheet("font-size: 48px;")
        self.back_button.clicked.connect(self.go_back)
        btn_layout.addWidget(self.back_button)

        self.remove_all = QPushButton("Remove All")
        self.remove_all.setFixedHeight(140)
        self.remove_all.setStyleSheet("font-size: 48px;")
        self.remove_all.clicked.connect(self.remove_all_plates)
        btn_layout.addWidget(self.remove_all)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plate_list)

    def showEvent(self, event: QEvent):
        super().showEvent(event)
        self.timer.start(500)

    def remove_all_plates(self):
        try:
            with open("plates/Seen_Plates.txt", "w") as f:
                pass
        except Exception as e:
            print(f"Error reading file: {e}")

    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)
        self.timer.stop()

    def update_plate_list(self):
        plates = []
        try:
            with open("plates/Seen_Plates.txt", "r") as f:
                plates = f.readlines()
            plates = [plate.strip() for plate in plates if plate.strip()]


            if plates:
                self.history_list.setText("\n".join(plates))
            else:
                self.history_list.setText("No Plates Input Yet")
            self.adjust_font(plates)

        except Exception as e:
            self.history_list.setText(f"Error reading file: {e}")

    def adjust_font(self, plates):
        num_lines = len(plates) if plates else 1  # Ensure we have at least 1 line

        # Calculate the font size so that the number of lines fits within the fixed height
        font_size = max(10, min(40, 300 // (num_lines * 2)))
        # Apply the font size to the label
        font = QFont("Arial", font_size)
        self.history_list.setFont(font)


class MainWindow(QStackedWidget):
    """Main window managing all screens."""
    def __init__(self, app):
        super().__init__()

        self.camera_screen = CameraFeed(self)
        self.menu_screen = MainMenu(self, app)
        self.plate_input_screen = LicensePlateInput(self)
        self.current_id_screen = CurrentIdentifications(self)
        self.history_screen = PlateHistory(self)
        self.input_history_screen = CurrentInputs(self)

        self.addWidget(self.menu_screen)  # Index 0
        self.addWidget(self.camera_screen)  # Index 1
        self.addWidget(self.plate_input_screen)  # Index 2
        self.addWidget(self.current_id_screen)  # Index 3
        self.addWidget(self.history_screen)  # Index 4
        self.addWidget(self.input_history_screen)

        self.setCurrentIndex(0)  # Start on the main menu
        self.setFixedHeight(480)
        self.setFixedWidth(800)
        self.showFullScreen()




# Run the PyQt app
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
