# E-Waste Object Detection & Intelligent Advisory System

This system uses YOLOv8x to detect 45 types of Electronic Waste and provides intelligent recycling advice, material composition analysis, and hazard warnings.

## 🚀 Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare Dataset**:
   Run the setup script to create the required directory structure:
   ```bash
   python setup_dataset.py
   ```
   This will create `../datasets/ewaste/train` and `../datasets/ewaste/valid`.
   
   **You must populate these folders with your images and labels.**
   - Images go in `images/`
   - Labels (YOLO format .txt) go in `labels/`
   
   **Tip for Precision (Hard Negative Mining):**
   To teach the model to ignore non-electronic objects (e.g., books, clothes), simply add images of these items to the `train/images` folder but **do not create a label file** for them (or create an empty one). YOLO will treat these as background samples, reducing false positives.

3. **Train the Model**:
   Configuration is in `data.yaml` and `train.py`.
   To start training (this will download `yolov8x.pt` automatically):
   ```bash
   python train.py
   ```
   *Note: Training on 45 classes with high resolution (1280px) requires a powerful GPU (16GB+ VRAM recommended).*

4. **Inference / Detection**:
   Once trained, use the detection script.
   
   **Webcam Demo:**
   ```bash
   python detect.py --source 0
   ```
   
   **Image/Video File:**
   ```bash
   python detect.py --source path/to/image.jpg
   ```
   (Note: By default it looks for weights in `ewaste_project/yolov8x_custom_ewaste/weights/best.pt`. If not found, it falls back to base YOLOv8x for testing, but classes will be incorrect.)

## 🧠 Intelligence Layer

The `intelligence_layer.py` module contains the database of recycling instructions.
It analyzes detections and provides:
- **Material Composition**: (e.g., Gold, Lithium, Plastic)
- **Recycling Type**: (e.g., Hazardous, High Value)
- **Carbon Recovery Benefit**: Estimated impact.
- **Hazard Flags**: Alerts for batteries, mercury, etc.

## 📂 Project Structure

- `data.yaml`: YOLOv8 dataset configuration.
- `train.py`: Training script with augmentations.
- `detect.py`: Inference script with Intelligence Layer.
- `intelligence_layer.py`: Logic for material analysis.
- `requirements.txt`: Python dependencies.
- `setup_dataset.py`: Helper to create folders.
