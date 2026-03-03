import os

def create_structure():
    base_path = "../datasets/ewaste"
    
    dirs = [
        "train/images",
        "train/labels",
        "valid/images",
        "valid/labels",
        "test/images",
        "test/labels"
    ]
    
    print(f"Creating dataset structure at {os.path.abspath(base_path)}...")
    
    for d in dirs:
        path = os.path.join(base_path, d)
        os.makedirs(path, exist_ok=True)
        print(f"Created: {path}")

    print("\nSUCCESS! Dataset structure created.")
    print("Now you must:")
    print(f"1. Put 1000-2000 images per class in {os.path.join(base_path, 'train/images')}")
    print(f"2. Put corresponding YOLO format .txt labels in {os.path.join(base_path, 'train/labels')}")
    print(f"3. Do the same for 'valid' sets.")
    print("4. Run 'python train.py' to start training.")

if __name__ == "__main__":
    create_structure()
