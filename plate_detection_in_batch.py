import os
from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image, ImageDraw
import torch

# Directory paths
input_dir = '/home/roadrunner/hf_vc_model/my_local_dataset/raw_images/'
output_dir = '/home/roadrunner/hf_vc_model/my_local_dataset/cropped_images'

# Ensure output directory exists
#os.makedirs(output_dir, exist_ok=True)

# Load model and processor once
processor = YolosImageProcessor.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection')
model = YolosForObjectDetection.from_pretrained('nickmuchi/yolos-small-finetuned-license-plate-detection')

# Process each image
for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):

        # Load image
        image_path = os.path.join(input_dir, filename)
        image = Image.open(image_path).convert("RGB")

        # Inference
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)

        # Post-process predictions
        target_sizes = torch.tensor([image.size[::-1]])
        
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes)[0]

        # Draw bounding boxes
        draw = ImageDraw.Draw(image)

        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            xmin, ymin, xmax, ymax = [int(coord) for coord in box]
            #draw.rectangle([(xmin, ymin), (xmax, ymax)], outline="red", width=3)
            cropped_plate = image.crop((xmin, ymin, xmax, ymax))

            # Save cropped plate explicitly
            cropped_path = os.path.join(output_dir, f"cropped_{filename}")
            width, height = cropped_plate.size
            if height > width:
                cropped_plate = cropped_plate.rotate(-90, expand=True)
            cropped_plate.save(cropped_path)

            print(f"Cropped and saved: {cropped_path}")
            #draw.text((xmin, ymin), f"License Plate: {score:.2f}", fill="yellow")
        
        # Save annotated image
        #output_path = os.path.join(output_dir, f"detected_{filename}")
        #image.save(output_path)

        #print(f"Processed and saved: {output_path}")
