import pytesseract  # Tesseract OCR module
import matplotlib.pyplot as plt
import cv2  # OpenCV module
import glob
import os

# Define the path for license plate images (recursively search for JPG files)
path_for_license_plates = "/home/roadrunner/hf_vc_model/my_local_dataset/cropped_images/cropped_IMG_2724.jpeg"

predicted_license_plates = []

for path_to_license_plate in glob.glob(path_for_license_plates, recursive=True):
    # Read the license plate image using OpenCV
    img = cv2.imread(path_to_license_plate)
    
    # Pass the image to Tesseract OCR with specified configuration
    predicted_result = pytesseract.image_to_string(
        img, 
        lang='eng', 
        config='--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    )
    
    # Clean the result by removing whitespace and unwanted characters
    filter_predicted_result = "".join(predicted_result.split()).replace(":", "").replace("-", "")
    
    predicted_license_plates.append(filter_predicted_result)

# Print out the predicted license plate texts
for pred in predicted_license_plates:
    print(pred)
