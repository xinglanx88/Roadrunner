import shutil
import os
import kagglehub
dest_path = "./my_local_dataset"
path = kagglehub.dataset_download("nickyazdani/license-plate-text-recognition-dataset")
shutil.copytree(path, dest_path, dirs_exist_ok=True)

print(f"Copied dataset to: {dest_path}")