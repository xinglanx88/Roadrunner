from ultralytics import YOLO
import threading
import cv2
import os
# from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image, ImageDraw
import shared
import torch
import time
import numpy as np

from fast_plate_ocr import ONNXPlateRecognizer
# from ultralytics.nn.tasks import DetectionModel

# Add the safe global so that torch.load can safely load the checkpoint.

# license_plate_detector.to('cuda')
latest = None
license_plate_detector = YOLO('bestnew.pt')
reader = ONNXPlateRecognizer('global-plates-mobile-vit-v2-model')

ready_event = threading.Event()
waiter = threading.Lock()
# torch.serialization.add_safe_globals([DetectionModel])



license_plates = [
    "MPJ4621",
    "MRF8217",
    "LPX8448",
    "2081AJU",
    "TUV4567"
]
def read_frame(capture):
    global latest, vid
    ready_event.wait()
    vid = capture
    if not capture.isOpened():
        print("Could not open video")
    while shared.vidgoing:
        ret, frame = vid.read()
        if not ret:
            # shared.vidgoing = False
            #break
            latest = None
            continue
        with waiter:
            latest = frame

output_dir = "./saved_frames"
os.makedirs(output_dir, exist_ok=True)

frame_counter = 0

def save_frame(frame):
    
    filename = os.path.join(output_dir, f"frame_{frame_counter}.jpg")
    cv2.imwrite(filename, frame)
    print(f"Saved {filename}")
def process_img():
    global frame_counter
    global latest, vid
    while shared.vidgoing:
        with waiter:
            if latest is None:
                continue
            frame = latest.copy()
            frame_counter += 1
            if frame_counter % 100 == 0:  # Save every 100th frame
                save_frame(frame)
        results = license_plate_detector.predict(frame, device='cuda')
        for r in results:
            boxes = r.boxes.xyxy
            # print(boxes)
            for i, box in enumerate(boxes.cpu().numpy()):
                x1, y1, x2, y2 = map(int, box)
                cropped_plate = frame[y1:y2, x1:x2]

                crop_filename = os.path.join(output_dir, f"plate_{frame_counter:06d}.jpg")
                cv2.imwrite(crop_filename, cropped_plate)

                gray_crop = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2GRAY)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                #saving the cropped plate
                
                text = reader.run(gray_crop)

                text = text[0].rstrip('_') if text else ''
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                shared.plate_frame = frame.copy()
                print("detected plate: ", text)


def startYolo(capture):

    ready_event.set()
    read = threading.Thread(target=read_frame, args=(capture,))
    process = threading.Thread(target=process_img)

    print("starting")


    return read, process

