from ultralytics import YOLO
import threading
import cv2
import os
# from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image, ImageDraw
import torch
import time
import numpy as np
from ultralytics.nn.tasks import DetectionModel
import tempfile
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


#only needed in PC:

#import onnxruntime as ort

# Use only CUDA and CPU (if GPU is supported)
#session = ort.InferenceSession("your_model.onnx", providers=[
#    'CUDAExecutionProvider',  # optional if you have GPU
#    'CPUExecutionProvider'
#])



# ----- Detection Model: YOLOS for license plate detection -----
#from transformers import YolosImageProcessor, YolosForObjectDetection
from fast_plate_ocr import ONNXPlateRecognizer
ocr_recognizer = ONNXPlateRecognizer('global-plates-mobile-vit-v2-model')
ready_event = threading.Event()

# Add the safe global so that torch.load can safely load the checkpoint.
torch.serialization.add_safe_globals([DetectionModel])
latest = None
waiter = threading.Lock()
#video_path = '/home/roadrunner/hf_vc_model/output.mp4' jetson version 
video_path = './my_local_dataset/IMG_3011.mp4' # PC version
print("Exists:", os.path.exists(video_path))
output_dir = './my_local_dataset/cropped_images2'
vidgoing = True
frame_num = 0
dur = time.time()
framect = 0

license_plate_detector = YOLO('bestnew.pt')
# license_plate_detector.to('cuda')
#vid = cv2.VideoCapture(video_path)
#vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
#if not vid.isOpened():
_ = license_plate_detector.predict(np.zeros((640, 640, 3), dtype=np.uint8), device='cuda')
_ = ocr_recognizer.run(np.zeros((40, 120), dtype=np.uint8))
ready_event.set()   
#    print("Could not open video")
#fps = vid.get(cv2.CAP_PROP_FPS)
#print(f"Frame rate: {fps}")
#total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
#print(f"Total frames: {total_frames}")

def read_frame():
    global latest, vidgoing, frame_num, fps, total_frames, vid
    ready_event.wait()
    vid = cv2.VideoCapture(video_path)
    vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
    if not vid.isOpened():
        print("Could not open video")
        total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = vid.get(cv2.CAP_PROP_FPS)
    print(f"Frame rate: {fps}")
    total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames: {total_frames}")
    frame_interval = 1.0 / (fps+0.0001)
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

license_plates = [
    "MPJ4621",
    "MRF8217",
    "LPX8448",
    "2081AJU",
    "TUV4567"
]
output_txt = "./detections.txt"
if os.path.exists(output_txt):
    os.remove(output_txt)


plate_counts = {plate: 0 for plate in license_plates}

def process_img():
    global latest, vidgoing, frame_num, dur, framect, plate_counts, prev_plate

    framect = 0
    while vidgoing:
        
        with waiter:
            if latest is None:
                continue
            frame = latest.copy()
            #on pc somehow it is rotated counter clockwise, so we rotate it clockwise
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        """
        if frame_num == 0 or frame_num % 10 == 0:
            cropped_path = os.path.join(output_dir, f"cropped_{frame_num}.jpg")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_pil.save(cropped_path)
        """
        frame_num += 1  # update frame counter after verifying we have a frame
        dur = time.time()
        
        # Predict license plates in this frame using YOLO detector
        results = license_plate_detector.predict(frame, device='cuda')
        prev_plate = None
        for r in results:
            boxes = r.boxes.xyxy
            for i, box in enumerate(boxes.cpu().numpy()):
                x1, y1, x2, y2 = map(int, box)
                cropped_plate = frame[y1:y2, x1:x2]
                
                # Convert cropped plate (BGR) to PIL Image (RGB)
                cropped_plate_rgb = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2RGB)
                cropped_plate_pil = Image.fromarray(cropped_plate_rgb)
                
                # Create a temporary file to save the cropped plate image
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    temp_filename = tmp.name
                cropped_plate_pil.save(temp_filename, format="JPEG")
                cropped_path = os.path.join(output_dir, f"cropped_{frame_num}.jpg")
                cropped_plate_pil.save(cropped_path)

                # Run OCR on the temporary file using your OCR recognizer
                ocr_result = ocr_recognizer.run(temp_filename)
                # Assume OCR result is a list and we take the first element; remove trailing underscores
                ocr_text = ocr_result[0].rstrip('_')
                
                # Only process results of length 7
                if len(ocr_text) <= 8 and len(ocr_text) >= 6:
                    # If plate already exists in dict, increment count; otherwise, initialize count 
                    # this is to track flase positives

                    #if ocr_text not in plate_counts:
                    #    plate_counts[ocr_text] = 0
                    # If previous plate is different, reset its count
                    if prev_plate is not None and prev_plate != ocr_text and prev_plate in plate_counts:
                        plate_counts[prev_plate] = 0
                    # Update the current plate's count and set as previous
                    if ocr_text in plate_counts:
                        plate_counts[ocr_text] += 1
                        prev_plate = ocr_text
                    
                    # If count reaches 5, report the plate and reset its count
                        if plate_counts[ocr_text] == 5:
                            # Report result with a fabricated location (modify as needed)
                            with open(output_txt, "a") as f:
                                f.write(f"Plate {ocr_text} found at location (X, Y) in frame {frame_num}\n")
                            # Reset the count so only consecutive detections lead to new reporting
                            plate_counts[ocr_text] = 0
                
                # Optionally, delete the temporary file if you don't need it
                os.remove(temp_filename)
                framect += 1
        dur = time.time() - dur
ready_event.set()
read = threading.Thread(target=read_frame)
process = threading.Thread(target=process_img)

read.start()
process.start()

read.join()
vidgoing = False
process.join()
vid.release()
print(plate_counts)
#print(f"Total frames recorded: {framect}")
#print(f"Total frames: {total_frames}")
#if(fps>0):

#    print(f'Frames processed per sec: {framect / (total_frames / fps)}')