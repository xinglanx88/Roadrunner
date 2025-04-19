import cv2
import torch

# Load the model
model = torch.load('ultralytics/yolov8', 'custom', path='/home/roadrunner/hf_vc_model/models/LP-detection.pt')

# Load the input image
img = cv2.imread('/home/roadrunner/hf_vc_model/my_local_dataset/raw_images/IMG_2723.jpeg')

# Preprocess the input image
img = cv2.resize(img, (640, 480))

# Run the model
results = model(img)

# Extract the cropped license plate image
license_plate_img = results.crop[0].cpu().numpy()
cv2.imwrite('detected_license_plate.jpg', license_plate_img)
