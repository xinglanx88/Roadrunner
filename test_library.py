import torch
import torchvision

print(torchvision.ops.nms)

print("PyTorch:", torch.__version__)           # must say 2.5.0
print("Torchvision:", torchvision.__version__) # 
print("CUDA available:", torch.cuda.is_available())  # should print True
print("GPU:", torch.cuda.get_device_name(0))