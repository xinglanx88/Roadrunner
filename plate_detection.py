import os
from transformers import YolosFeatureExtractor, YolosForObjectDetection
from PIL import Image
import torch

# Setup YOLOS model
feature_extractor = YolosFeatureExtractor.from_pretrained(
    'nickmuchi/yolos-small-finetuned-license-plate-detection')
model = YolosForObjectDetection.from_pretrained(
    'nickmuchi/yolos-small-finetuned-license-plate-detection')#.to('cuda')

# Directory containing images
image_dir = "/home/roadrunner/hf_vc_model/my_local_dataset/raw_images"
output_dir = "/home/roadrunner/hf_vc_model/my_local_dataset/cropped_images"

os.makedirs(output_dir, exist_ok=True)

# Get list of image paths
exts = [".jpg", ".jpeg", ".png"]
image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir)
               if os.path.splitext(f)[-1].lower() in exts]

# Load images
images = [Image.open(path).convert("RGB") for path in image_paths]
sizes = [img.size for img in images]

# Prepare inputs for batch inference
inputs = feature_extractor(images=images, return_tensors="pt").to('cuda')

# Run YOLOS inference in batch
with torch.no_grad():
    outputs = model(**inputs)

logits = outputs.logits
bboxes = outputs.pred_boxes

# Loop through each image in the batch
for idx, (logit, bbox, size, img, path) in enumerate(zip(logits, bboxes, sizes, images, image_paths)):
    width, height = size
    
    # Post-process predictions
    probs = logit.softmax(-1)[:, :-1]  # remove "no-object"
    scores, labels = probs.max(-1)
    
    # Select the highest-scoring detection
    best_idx = scores.argmax().item()
    best_bbox = bbox[best_idx]
    print(bbox)
    print("best_idx: ", best_idx)
    # Convert to absolute coordinates
    xmin, ymin, xmax, ymax = best_bbox.cpu().numpy()
    xmin, ymin, xmax, ymax = best_bbox.cpu().numpy()
    xmin = max(0, int(xmin * width))
    ymin = max(0, int(ymin * height))
    xmax = min(width, int(xmax * width))
    ymax = min(height, int(ymax * height))

# Ensure the crop is valid
    if xmax <= xmin or ymax <= ymin:
        print(f"Invalid bbox for {path}, skipping crop.")
        continue
    # Crop the detected license plate
    cropped_plate = img.crop((xmin, ymin, xmax, ymax))

    # Save cropped license plate
    basename = os.path.basename(path)
    save_path = os.path.join(output_dir, f"cropped_{basename}")
    cropped_plate.save(save_path)

    print(f"Cropped {basename} => {save_path}")
