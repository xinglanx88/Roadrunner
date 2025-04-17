from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image
import torch
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Check for CUDA
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Running on:", device)

# Load model and move to CUDA
model = VisionEncoderDecoderModel.from_pretrained("./local_ocr_model").to(device)

# Load processor components (these stay on CPU — only their outputs matter)
image_processor = ViTImageProcessor.from_pretrained("./local_ocr_model")
tokenizer = AutoTokenizer.from_pretrained("./local_ocr_model")

# Load and preprocess image
image = Image.open("/home/roadrunner/hf_vc_model/my_local_dataset/cropped_lps/cropped_lps/37399.jpg").convert("RGB")
pixel_values = image_processor(images=image, return_tensors="pt").pixel_values.to(device)

# Generate and decode prediction
with torch.no_grad():
    generated_ids = model.generate(pixel_values)

prediction = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print("Predicted License Plate:", prediction)
