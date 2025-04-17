from datasets import load_dataset

ds = load_dataset("keremberke/license-plate-object-detection", "mini")

ds.save_to_disk("./my_local_dataset")