from ultralytics import YOLO
import torch

def train_model():
    # 1. Load the model. 
    # Using yolov8x.pt (Extra Large) for maximum accuracy as requested.
    # It will automatically download if not present.
    print("Loading YOLOv8x model...")
    model = YOLO('yolov8x.pt') 

    # 2. Training Configuration
    # The user requested specific strong augmentations and training parameters.
    # These are passed to the train() method.
    
    print("Starting training...")
    try:
        results = model.train(
            data='data.yaml',
            epochs=150,
            patience=20,           # Early stopping patience
            batch=16,              # Adjust based on GPU memory (8 or 4 if OOM)
            imgsz=1280,            # High resolution for small components
            optimizer='AdamW',     # Requested optimizer
            lr0=0.001,             # Initial learning rate
            
            # Augmentation Hyperparameters (Strong)
            degrees=25.0,          # Rotation +/- 25 deg
            translate=0.1,         # Translation
            scale=0.5,             # Scale gain
            shear=0.0,
            perspective=0.0,
            flipud=0.0,
            fliplr=0.5,            # Horizontal flip 50%
            mosaic=1.0,            # Mosaic augmentation (strong)
            mixup=0.15,            # Mixup (good for clutter)
            copy_paste=0.1,        # Copy-paste segmentations
            hsv_h=0.015,           # HSV Hue
            hsv_s=0.7,             # HSV Saturation
            hsv_v=0.4,             # HSV Value (Brightness/Contrast)
            
            # System
            device=0 if torch.cuda.is_available() else 'cpu',
            workers=8,
            project='ewaste_project',
            name='yolov8x_custom_ewaste',
            exist_ok=True,
            
            # Validation
            val=True,
            save=True
        )
        print("Training complete. Best model saved in ewaste_project/yolov8x_custom_ewaste/weights/best.pt")
        
    except Exception as e:
        print(f"Error during training: {e}")
        print("Make sure your dataset is structured correctly in ../datasets/ewaste")

if __name__ == '__main__':
    train_model()
