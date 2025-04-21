from datasets import load_dataset

# Login using e.g. `huggingface-cli login` to access this dataset
#ds = load_dataset("./my_local_dataset/EZCon/taiwan-license-plate-recognition")


from ultralytics import YOLO

import cv2
import os
# from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image, ImageDraw
import torch

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

# Add the safe global so that torch.load can safely load the checkpoint.

#video_path = '/home/roadrunner/hf_vc_model/output.mp4' jetson version 


license_plate_detector = YOLO('bestnew.pt')
correct = 0
total = 0
frame_num = 0
plate_counts = {}
prev_plate = None

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

out_path = "plate_eval_results.txt"

def process_dataset_for_accuracy(ocr_recognizer):
    ds = load_dataset("EZCon/taiwan-license-plate-recognition")
    test_set = ds["train"]  # Or "train" or "validation"
    
    correct = 0
    total = 0

    for idx, sample in enumerate(test_set):
        image_pil = sample["image"]
        true_plate = sample["license_number"].replace("-", "").strip().upper()

        rgb_img = np.array(image_pil.convert("RGB"))  # Convert PIL image to RGB

        # Convert RGB -> BGR (OpenCV format for YOLO)
        bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)

        # Now pass to YOLO
        results = license_plate_detector.predict(bgr_img, device="cuda")
        r= results[0]
        if r.boxes is None or len(r.boxes) == 0:
            continue
        # Get the bounding boxes and labels
        boxes = r.boxes.xyxy

        # Crop the license plate area
        is_correct = False


        for i, box in enumerate(boxes.cpu().numpy()):
                
                x1, y1, x2, y2 = map(int, box)
                cropped_plate_pil = image_pil.crop((x1, y1, x2, y2))

                
                # Convert cropped plate (BGR) to PIL Image (RGB)
                
                
                # Create a temporary file to save the cropped plate image
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    temp_filename = tmp.name
                cropped_plate_pil.save(temp_filename, format="JPEG")
                

        # Run OCR
                ocr_result = ocr_recognizer.run(temp_filename)
                os.remove(temp_filename)

                if not ocr_result:
                    continue

                ocr_text = ocr_result[0].replace("-", "").strip().upper().rstrip('_')
                print(f"Detected plate: {ocr_text}")
                print(f"True plate: {true_plate}")
                # Check if the OCR result is valid
                # Basic length filter
                if 6 <= len(ocr_text) <= 8:
                    is_correct = False

                    if ocr_text == true_plate:
                        is_correct = True
                    elif len(ocr_text) == len(true_plate):
                        # count mismatches and capture the differing pair
                        diff_positions = [(p, l) for p, l in zip(ocr_text, true_plate) if p != l]
                        if len(diff_positions) == 1:
                            # exactly one mismatch, check if that pair is a known confusion
                            if diff_positions[0] in confusions:
                                is_correct = True
                    if is_correct :
                        correct += 1
                        break
        with open(out_path, "a", encoding="utf‑8") as f:
            f.write(f"{idx}  \tPredicted plate: {ocr_text} \t True plate: {true_plate}\n")
        total += 1

    
    accuracy = correct / total if total > 0 else 0
    with open(out_path, "a", encoding="utf‑8") as f:
        f.write(f"\n# Accuracy: {accuracy:.2%}  ({correct}/{total})\n")
    print(f"\n🎯 OCR Accuracy : {accuracy:.2%} ({correct}/{total})")

process_dataset_for_accuracy(ocr_recognizer)
