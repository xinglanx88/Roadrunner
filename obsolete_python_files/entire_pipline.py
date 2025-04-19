import os
import torch
from gpsNMEA import gpsNMEA
from transformers import (
    YolosImageProcessor, 
    YolosForObjectDetection,
    VisionEncoderDecoderModel, 
    ViTImageProcessor, 
    AutoTokenizer
)
from PIL import Image

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Device check
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Directory containing raw images
raw_image_dir = "/home/roadrunner/hf_vc_model/my_local_dataset/raw_images/"

# Load detection model
det_processor = YolosImageProcessor.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection')
det_model = YolosForObjectDetection.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection').to(device)

# Load OCR model in FP16
ocr_model = VisionEncoderDecoderModel.from_pretrained("DunnBC22/trocr-base-printed_license_plates_ocr").half().to(device)
ocr_processor = ViTImageProcessor.from_pretrained("microsoft/trocr-base-printed")
tokenizer = AutoTokenizer.from_pretrained("microsoft/trocr-base-printed")

# Process each raw image
for filename in os.listdir(raw_image_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(raw_image_dir, filename)
        image = Image.open(image_path).convert("RGB")

        # Detection step
        inputs = det_processor(images=image, return_tensors="pt").to(device)
        outputs = det_model(**inputs)

        # Post-process detections to get bounding boxes
        target_sizes = torch.tensor([image.size[::-1]])
        results = det_processor.post_process_object_detection(outputs, target_sizes=target_sizes)[0]

        cropped_images = []

        # Crop detected license plates directly into memory
        for idx, box in enumerate(results["boxes"]):
            xmin, ymin, xmax, ymax = [int(coord) for coord in box]

            cropped_plate = image.crop((xmin, ymin, xmax, ymax))
            width, height = cropped_plate.size
            if height > width:
                cropped_plate = cropped_plate.rotate(-90, expand=True)
            cropped_images.append(cropped_plate)

        # Perform OCR directly on cropped plates
        if cropped_images:
            ocr_inputs = ocr_processor(images=cropped_images, return_tensors="pt").pixel_values.half().to(device)

            with torch.no_grad():
                generated_ids = ocr_model.generate(ocr_inputs, max_length=7, min_length=7)

            predictions = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

            # Print results clearly
            for idx, pred in enumerate(predictions):
                #print(f"{filename} (plate {idx}) => {pred}")
                print(pred)
                print("found at: ")
                gpsNMEA()
        else:
            print(f"{filename}: No plates detected.")
