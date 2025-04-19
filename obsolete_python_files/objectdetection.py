from ultralytics import YOLO
import cv2
import os
from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image, ImageDraw
import torch
import time
import numpy as np
# from ultralytics.nn.tasks import DetectionModel


# torch.serialization.add_safe_globals([DetectionModel])
# Directory paths
input_dir = '/home/roadrunner/hf_vc_model/my_local_dataset/raw_images/'
output_dir = '/home/roadrunner/hf_vc_model/my_local_dataset/cropped_images'

# Load model and processor once
license_plate_detector = YOLO('best.pt')

# Process each image
for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        imloadtime = time.time()
        # Load image
        image_path = os.path.join(input_dir, filename)
        image = Image.open(image_path).convert("RGB")
        # image = image.resize((640, 480))
        results = license_plate_detector.predict(image)
        for r in results:
            boxes = r.boxes.xyxy
            print(boxes)
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                print(x1,y1,x2,y2)
                cropped_plate = image.crop((x1, y1, x2, y2))

                # Save cropped plate explicitly
                cropped_path = os.path.join(output_dir, f"cropped_{filename}")
                width, height = cropped_plate.size
                if height > width:
                    cropped_plate = cropped_plate.rotate(-90, expand=True)
                cropped_plate.save(cropped_path)

                print(f"Cropped and saved: {cropped_path}")