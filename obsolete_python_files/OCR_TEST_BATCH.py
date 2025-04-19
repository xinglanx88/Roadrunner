import os
from PIL import Image
import torch
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import warnings
import logging

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Use GPU if available
if(torch.cuda.is_available()):
    print("using CUDA")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model in half precision (FP16)
model = VisionEncoderDecoderModel.from_pretrained("DunnBC22/trocr-base-printed_license_plates_ocr").half().to(device)
image_processor = ViTImageProcessor.from_pretrained("microsoft/trocr-base-printed")
tokenizer = AutoTokenizer.from_pretrained("microsoft/trocr-base-printed")

# Directory of images
image_dir = "/home/roadrunner/hf_vc_model/my_local_dataset/batch_of_plates"

# Supported extensions
exts = [".jpg", ".jpeg", ".png"]

# Gather image paths
image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if os.path.splitext(f)[-1].lower() in exts]

# Load images and preprocess
images = [Image.open(p).convert("RGB") for p in image_paths]
inputs = image_processor(images=images, return_tensors="pt").pixel_values.half().to(device)

# Inference
with torch.no_grad():
    generated_ids = model.generate(inputs, max_length=8, min_length=7)

# Decode predictions
predictions = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

# Print results
for path, pred in zip(image_paths, predictions):
    print(f"{os.path.basename(path)} => {pred}")
