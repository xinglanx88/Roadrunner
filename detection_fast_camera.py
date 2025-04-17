from ultralytics import YOLO
import threading
import cv2
import os
from fast_plate_ocr import ONNXPlateRecognizer
# from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image, ImageDraw
import torch
import time
import numpy as np
from ultralytics.nn.tasks import DetectionModel

# Add the safe global so that torch.load can safely load the checkpoint.
torch.serialization.add_safe_globals([DetectionModel])
ready_event = threading.Event()
latest = None
waiter = threading.Lock()
video_path = '/home/roadrunner/hf_vc_model/my_local_dataset/output.mov'
print("Exists:", os.path.exists(video_path))
output_dir = '/home/roadrunner/hf_vc_model/my_local_dataset/cropped_images2'
vidgoing = True
frame_num = 0
dur = time.time()
framect = 0

license_plate_detector = YOLO('bestnew.pt')

vid = cv2.VideoCapture("/dev/video0")
if not vid.isOpened():
    print("Could not open video")
fps = vid.get(cv2.CAP_PROP_FPS)
print(f"Frame rate: {fps}")
total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
m = ONNXPlateRecognizer('global-plates-mobile-vit-v2-model')
# license_plate_detector.to('cuda')
ready_event.set()
def read_frame():
    global latest, vidgoing, frame_num, vid
    ready_event.wait()
    frame_interval = 1.0 / (fps+0.0001) #added 0.0001 to avoid division by 0n
    while vidgoing:
        started = time.time()
        ret, frame = vid.read()
        if not ret:
            vidgoing = False
            break
        frame_num = int(vid.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        with waiter:
            latest = frame
        elapsed = time.time() - started
        wait_time = frame_interval - elapsed
        if wait_time > 0:
            time.sleep(wait_time)
        # time.sleep(0.1)

def process_img():
    global latest, vidgoing, frame_num, dur, framect, total_frames
    framect = 0
    while vidgoing:
        with waiter:
            if latest is None:
                continue
            frame_num += 1
            frame = latest.copy()
        dur = time.time()
        results = license_plate_detector.predict(frame, device='cuda')
        for r in results:
            boxes = r.boxes.xyxy
            # print(boxes)
            for i, box in enumerate(boxes.cpu().numpy()):
                x1, y1, x2, y2 = map(int, box)
                # print(x1,y1,x2,y2)
                cropped_plate = frame[y1:y2, x1:x2]
                filename = os.path.join(output_dir, f"frame{frame_num}_plate{i}.jpg")
                gray_crop = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2GRAY)
                # cv2.imwrite(filename, cropped_plate)
                text = m.run(gray_crop)[0].rstrip('_')
                with open("detected_plate.txt", "a") as file:
                    file.write(f"{text}\n")
                print(text)
                print(f"Cropped and saved")
            if framect == 0:
                total_frames = total_frames - frame_num
            framect += 1
        dur = time.time() - dur
        print(dur)

read = threading.Thread(target=read_frame)
process = threading.Thread(target=process_img)

read.start()
process.start()

read.join()
vidgoing = False
process.join()
vid.release()
print(f"Total frames recorded: {framect}")
print(f"Total frames: {total_frames}")
if(fps>0):

    print(f'Frames processed per sec: {framect / (total_frames / fps)}')