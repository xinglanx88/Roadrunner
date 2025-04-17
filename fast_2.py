import os
import time
import torch
from fast_alpr import ALPR

# Set environment variable so CUDA is visible (if not already)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# Initialize ALPR with custom plate detection and OCR models.
alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="global-plates-mobile-vit-v2-model",
    ocr_device="cuda"
)

# If fast_alpr is built on top of PyTorch models, try to move them to CUDA.
# This assumes that fast_alpr creates attributes named 'detector' and 'ocr'


#print("Using device:", "cuda" if torch.cuda.is_available() else "cpu")
# Define the directory containing your raw images.
image_dir = "/home/roadrunner/hf_vc_model/my_local_dataset/raw_images/"

# Gather all image file paths in the directory (you can extend to other extensions if needed)
image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir)
               if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# Process each image in the batch
for image_path in image_paths:
    imloadtime = time.time()
    result = alpr.predict(image_path)
    plate_text = result[0].ocr.text
    print(plate_text)
    imloadtime = time.time()-imloadtime
    print("time processing = ",  imloadtime)

