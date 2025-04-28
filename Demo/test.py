import sys
sys.path.append('/usr/lib/python3.10/dist-packages')
import cv2

# Define GStreamer pipeline for IMX477 camera
gstreamer_pipeline = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM), width=1920, height=1080, framerate=60/1 ! "
    "nvvidconv ! "
    "video/x-raw, format=BGRx ! "  # Convert to BGRx (RGB-like format)
    "appsink"
)

# Open the video capture with the GStreamer pipeline
cap = cv2.VideoCapture(gstreamer_pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Failed to open camera!")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame!")
        break

    # Display the resulting frame
    cv2.imshow('IMX477 Camera Feed', frame)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture object and close windows
cap.release()
cv2.destroyAllWindows()
