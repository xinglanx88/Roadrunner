import os
import torch
import numpy as np
from PIL import Image
import warnings
import tempfile
#from gpsNMEA import gpsNMEA

# Suppress warnings
warnings.filterwarnings("ignore")

# Device check
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Directory containing raw images
raw_image_dir = "/home/roadrunner/hf_vc_model/my_local_dataset/raw_images/"

# ----- Detection Model: YOLOS for license plate detection -----
from transformers import YolosImageProcessor, YolosForObjectDetection
det_processor = YolosImageProcessor.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection')
det_model = YolosForObjectDetection.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection').to(device)

# ----- OCR Model: ONNX-based plate recognizer -----
from fast_plate_ocr import ONNXPlateRecognizer
ocr_recognizer = ONNXPlateRecognizer('global-plates-mobile-vit-v2-model')

# ----- Integrated Processing -----
# For each raw image, detect license plates, crop them in memory,
# rotate if necessary, and run OCR using the ONNX recognizer.
for filename in os.listdir(raw_image_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(raw_image_dir, filename)
        image = Image.open(image_path).convert("RGB")

        # Detection step: run YOLOS to get bounding boxes
        inputs = det_processor(images=image, return_tensors="pt").to(device)
        outputs = det_model(**inputs)

        # Convert YOLOS outputs (normalized) to absolute pixel coordinates:
        target_sizes = torch.tensor([image.size[::-1]])  # (height, width)
        results_det = det_processor.post_process_object_detection(outputs, target_sizes=target_sizes)[0]

        # Process each detected bounding box
        for idx, box in enumerate(results_det["boxes"]):
            xmin, ymin, xmax, ymax = [int(coord) for coord in box]
            cropped_plate = image.crop((xmin, ymin, xmax, ymax))
            
            # Check aspect ratio: if vertical (height > width), rotate 90° clockwise
            width, height = cropped_plate.size
            if height > width:
                cropped_plate = cropped_plate.rotate(-90, expand=True)
            
            # Save the cropped image to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                temp_filename = tmp.name
                cropped_plate.save(temp_filename, format="JPEG")
            
            # Run OCR on the temporary file using the ONNX recognizer
            ocr_result = ocr_recognizer.run(temp_filename)
            
            # Print the result
            print(ocr_result)
            print("found at: ")
            #gpsNMEA()

            
            # Remove the temporary file
            os.remove(temp_filename)
