
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
# load model
model = yolov5.load('keremberke/yolov5m-license-plate').to('cuda')
  
# set model parameters
model.conf = 0.25  # NMS confidence threshold
model.iou = 0.45  # NMS IoU threshold
model.agnostic = False  # NMS class-agnostic
model.multi_label = False  # NMS multiple labels per box
model.max_det = 1000  # maximum number of detections per image

# set image
img = '/home/roadrunner/hf_vc_model/my_local_dataset/raw_images/CarLongPlateGen499_jpg.rf.3b65481c7c000871d647d08e185f0f7b.jpg'

# perform inference
results = model(img, size=640)

# inference with test time augmentation
#results = model(img, augment=True)

# parse results
predictions = results.pred[0]
boxes = predictions[:, :4] # x1, y1, x2, y2
scores = predictions[:, 4]
categories = predictions[:, 5]

img_cv = cv2.imread(img)


# show detection bounding boxes on image
for box, score, cat in zip(boxes, scores, categories):
    x1, y1, x2, y2 = x1, y1, x2, y2 = box.cpu().numpy().astype(int)
    cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
    label = f"Plate {score:.2f}"
    cv2.putText(img_cv, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, (0, 255, 0), 2)

# Save the image manually (ensure write permissions to directory)
save_path = '/home/roadrunner/hf_vc_model/my_local_dataset/cropped_images/detection.jpg'
cv2.imwrite(save_path, img_cv)

print(f"Detection image saved to: {save_path}")