import os
from PIL import Image
import torch
from transformers import AutoTokenizer, ViTImageProcessor, VisionEncoderDecoderModel
import warnings
import logging

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Use GPU if available
if torch.cuda.is_available():
    print("using CUDA")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model and processor
model = VisionEncoderDecoderModel.from_pretrained("artbreguez/trocr-base-printed_license_plates_ocr").half().to(device)
image_processor = ViTImageProcessor.from_pretrained("microsoft/trocr-base-printed")
tokenizer = AutoTokenizer.from_pretrained("microsoft/trocr-base-printed")

# Directory of images
image_dir = "/home/roadrunner/hf_vc_model/my_local_dataset/cropped_images"

# Supported extensions
exts = [".jpg", ".jpeg", ".png"]

# Gather image paths
image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if os.path.splitext(f)[-1].lower() in exts]

# Load and process images
images = [Image.open(p).convert("RGB") for p in image_paths]
inputs = image_processor(images=images, return_tensors="pt").to(device)

# Generate predictions
with torch.no_grad():
    generated_ids = model.generate(**inputs, max_length=7, min_length=7)

# Decode predictions
predictions = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

# Output
for path, pred in zip(image_paths, predictions):
    print(f"{os.path.basename(path)} => {pred}")
