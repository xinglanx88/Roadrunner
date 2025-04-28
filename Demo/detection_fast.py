from ultralytics import YOLO
import sys
sys.path.append('/usr/lib/python3.10/dist-packages')
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
output_txt = "./detections.txt"
# license_plate_detector.to('cuda')
latest = None
license_plate_detector = YOLO('bestnew.pt')
reader = ONNXPlateRecognizer('global-plates-mobile-vit-v2-model')

ready_event = threading.Event()
waiter = threading.Lock()
# torch.serialization.add_safe_globals([DetectionModel])

confusions = {
    # digits vs. letters that share nearly identical glyphs
    ('0', 'O'), ('O', '0'),
    ('0', 'D'), ('D', '0'),
    ('0', 'Q'), ('Q', '0'),
    ('1', 'I'), ('I', '1'),
    ('1', 'L'), ('L', '1'),
    ('2', 'Z'), ('Z', '2'),
    ('3', 'E'), ('E', '3'),
    ('4', 'A'), ('A', '4'),
    ('5', 'S'), ('S', '5'),
    ('6', 'G'), ('G', '6'),
    ('6', 'B'), ('B', '6'),
    ('7', 'T'), ('T', '7'),
    ('8', 'B'), ('B', '8'),
    ('9', 'G'), ('G', '9'),
    ('9', 'Q'), ('Q', '9'),

    # letters easily confused with other letters
    ('C', 'G'), ('G', 'C'),
    ('C', 'O'), ('O', 'C'),
    ('D', 'O'), ('O', 'D'),
    ('F', 'P'), ('P', 'F'),
    ('H', 'N'), ('N', 'H'),
    ('M', 'N'), ('N', 'M'),
    ('U', 'V'), ('V', 'U'),
    ('V', 'Y'), ('Y', 'V'),
    ('W', 'VV'), ('VV', 'W'),   # some OCR models split W into “VV”

    # common stylised or worn‑print errors
    ('K', 'X'), ('X', 'K'),
    ('8', '0'), ('0', '8'),     # thick fonts blur holes
    ('B', 'R'), ('R', 'B'),     # chipped print can open/close loops
}



license_plates = [
    "MPJ4621",
    "MRF8217",
    "LPX8448",
    "2081AJU",
    "TUV4567"
]
plate_counts = {plate: 0 for plate in license_plates}
def read_frame(capture):
    print("read_frame thread started")
    global latest, vid
    ready_event.wait()
    vid = capture
    if not capture.isOpened():
        print("Could not open video")
    while shared.vidgoing:
        ret, frame = vid.read()
        if ret:
            print("✅ Frame received")
            with waiter:
                latest = frame
        else:
            print("⚠️ Frame read failed, retrying…")

output_dir = "./saved_frames"
os.makedirs(output_dir, exist_ok=True)

frame_counter = 0


def is_confusable(plate1, plate2):
    """
    Determines if two plate strings are considered equivalent,
    accounting for common OCR confusions.
    """
    if len(plate1) != len(plate2):
        return False

    for c1, c2 in zip(plate1, plate2):
        if c1 == c2:
            continue
        if (c1, c2) not in confusions:
            return False
    return True


def save_frame(frame):
    
    filename = os.path.join(output_dir, f"frame_{frame_counter}.jpg")
    cv2.imwrite(filename, frame)
    print(f"Saved {filename}")
def process_img():
    print("process_img thread started")
    print("video going: ", shared.vidgoing)
    ##############
    # Process the image
    ##############
    # global license_plate_detector
    global frame_counter
    global latest, vid
    while shared.vidgoing:
        #print("processing")
        
        with waiter:
            if latest is None:
                continue
            frame = latest.copy()
            frame_counter += 1
            if frame_counter % 100 == 0:  # Save every 100th frame
                save_frame(frame)
        results = license_plate_detector.predict(frame, device='cuda')
        prev_plate = None
        for r in results:
            boxes = r.boxes.xyxy
            # print(boxes)
            for i, box in enumerate(boxes.cpu().numpy()):
                x1, y1, x2, y2 = map(int, box)
                cropped_plate = frame[y1:y2, x1:x2]

                # crop_filename = os.path.join(output_dir, f"plate_{frame_counter:06d}.jpg")
                # cv2.imwrite(crop_filename, cropped_plate)

                gray_crop = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2GRAY)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                #saving the cropped plate
                
                text = reader.run(gray_crop)

                text = text[0].rstrip('_') if text else ''


                #getting a 5 frame count
                ocr_text = text
                if len(ocr_text) <= 8 and len(ocr_text) >= 6:
                    # If plate already exists in dict, increment count; otherwise, initialize count 
                    # this is to track flase positives

                    #if ocr_text not in plate_counts:
                    #    plate_counts[ocr_text] = 0
                    # If previous plate is different, reset its count
                    matched_plate = None
                    for ref_plate in plate_counts.keys():
                        if text == ref_plate or is_confusable(text, ref_plate):
                            matched_plate = ref_plate
                            break

                    if matched_plate:
                        # Reset previous plate if necessary
                        if prev_plate is not None and prev_plate != matched_plate and prev_plate in plate_counts:
                            plate_counts[prev_plate] = 0

                        plate_counts[matched_plate] += 1
                        prev_plate = matched_plate

                        if plate_counts[matched_plate] == 5:
                            with open(output_txt, "a") as f:
                                f.write(f"Plate {matched_plate} confirmed at location (X, Y) after 5 detections\n")
                            plate_counts[matched_plate] = 0

                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                print("detected plate: ", text)
            shared.plate_frame = frame.copy()



def startYolo(capture):

    #ready_event.set()

    read = threading.Thread(target=read_frame, args=(capture,))
    process = threading.Thread(target=process_img)
    shared.vidgoing = True 
    ready_event.set()  
    print("starting")


    return read, process

