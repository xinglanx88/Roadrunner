from transformers import YolosFeatureExtractor, YolosForObjectDetection,  YolosImageProcessor
from PIL import Image , ImageDraw
import requests
import torch 
image_path = '/home/roadrunner/hf_vc_model/my_local_dataset/raw_images/plate_photo.jpg'
image = Image.open(image_path).convert("RGB")

processor = YolosImageProcessor.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection')
feature_extractor = YolosFeatureExtractor.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection')
model = YolosForObjectDetection.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection')
inputs = feature_extractor(images=image, return_tensors="pt")
outputs = model(**inputs)

# model predicts bounding boxes and corresponding face mask detection classes
logits = outputs.logits
bboxes = outputs.pred_boxes


target_sizes = torch.tensor([image.size[::-1]])  # (height, width)
results = processor.post_process_object_detection(outputs, target_sizes=target_sizes)[0]

# Draw bounding boxes on the original image
draw = ImageDraw.Draw(image)

for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    xmin, ymin, xmax, ymax = box
    draw.rectangle([(xmin, ymin), (xmax, ymax)], outline="red", width=3)
   # draw.text((xmin, ymin), f"License Plate: {score:.2f}", fill="yellow")

# Show the image with bounding boxes
#image.show()
image.save("/home/roadrunner/hf_vc_model/detected_license_plate.jpg")