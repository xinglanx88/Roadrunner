Use of each files: 

bestnew.pt: the model loaded for plate detection
detection_fast.py: video reading with detection and character recognition
detection_fast_camer.py: camera stream reading with detection and character recognition 
fast_pipeline_final.py: video reading with detection and character recognition and 5 frames confirmation
pc_fast_pipeline.py: video reading with detection and character recognition and 5 frames confirmation that runs on PC with frames rotated clockwise for 90 degree because the current frame reading of the  test video has the frame rotated counterclockwise by 90
gpsNMEA.py: contains a function that output the GPS locations, only tested on Jetson with the GPS module attached.
install all the dependencies with pip install -r requirements.txt
