#from transformers import pipeline
#pipe = pipeline("image-to-text", model="DunnBC22/trocr-base-printed_license_plates_ocr")
#print(pipe("/home/roadrunner/hf_vc_model/my_local_dataset/cropped_lps/cropped_lps/37399.jpg"))
from transformers import VisionEncoderDecoderModel, TrOCRProcessor, ViTImageProcessor, AutoTokenizer
from PIL import Image
import torch
import warnings
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

warnings.filterwarnings("ignore", category=FutureWarning)

# Load model and processor manually
model = VisionEncoderDecoderModel.from_pretrained("DunnBC22/trocr-base-printed_license_plates_ocr").half().to("cuda")

# Later:
#processor = TrOCRProcessor.from_pretrained("DunnBC22/trocr-base-printed_license_plates_ocr")

image_processor = ViTImageProcessor.from_pretrained("microsoft/trocr-base-printed")
tokenizer = AutoTokenizer.from_pretrained("microsoft/trocr-base-printed")
# Load your image
image = Image.open("/home/roadrunner/hf_vc_model/my_local_dataset/cropped_lps/cropped_lps/37399.jpg").convert("RGB")
pixel_values = image_processor(images=image, return_tensors="pt").pixel_values.half().to("cuda")

# Generate and decode prediction
generated_ids = model.generate(pixel_values)
prediction = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print("Predicted License Plate:", prediction)