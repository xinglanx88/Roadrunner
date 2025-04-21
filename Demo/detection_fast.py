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
# from ultralytics.nn.tasks import DetectionModel

# Add the safe global so that torch.load can safely load the checkpoint.

# license_plate_detector.to('cuda')
latest = None
license_plate_detector = YOLO('bestnew.pt')


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
            shared.vidgoing = False
            break
        with waiter:
            latest = frame


def process_img():
    global latest, vid
    while shared.vidgoing:
        with waiter:
            if latest is None:
                continue
            frame = latest.copy()
        results = license_plate_detector.predict(frame, device='cuda')
        for r in results:
            boxes = r.boxes.xyxy
            # print(boxes)
            for i, box in enumerate(boxes.cpu().numpy()):
                x1, y1, x2, y2 = map(int, box)
                cropped_plate = frame[y1:y2, x1:x2]
                gray_crop = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2GRAY)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                text = reader.readtext(gray_crop, detail=0)
                text = text[0].rstrip('_') if text else ''
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                shared.plate_frame = frame.copy()
                print(text)


def startYolo(capture):

    ready_event.set()
    read = threading.Thread(target=read_frame, args=(capture,))
    process = threading.Thread(target=process_img)

    print("starting")


    return read, process

