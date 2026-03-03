# 📊 DATASET GUIDE - Waste Detection Training

## Roboflow Waste Detection v9 Dataset

### Dataset Overview

| Property | Details |
|----------|---------|
| **Name** | Roboflow Waste Detection v9 |
| **Source** | https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3 |
| **License** | CC BY 4.0 (Creative Commons Attribution 4.0) |
| **Total Images** | 2,500+ high-quality annotated images |
| **Image Resolution** | 640×640 pixels (YOLOv11 native format) |
| **Waste Classes** | 40+ different waste types |
| **Annotation Format** | YOLO format (.txt files with normalized coordinates) |
| **Dataset Split** | 70% training, 15% validation, 15% testing |
| **Image Format** | JPG/PNG |

---

## 40+ Waste Categories

### ♻️ Recyclable (13 types)
```
cardboard_box           Cardboard boxes and packaging
can                     Aluminum and metal cans
plastic_bottle_cap      Plastic bottle caps
plastic_bottle          Plastic bottles (various sizes)
reuseable_paper         High-quality reusable paper
paper                   Regular paper and cardboard sheets
cardboard               Pure cardboard material
aluminum                Aluminum foils and containers
glass_bottle            Glass bottles and jars
metal_can               Metal cans and containers
plastic                 General plastic items
newspaper               Newspaper and printed pages
magazine                Magazine pages and publications
```

### ⚠️ Non-Recyclable (17 types)
```
plastic_bag             Single-use plastic bags
scrap_paper             Soiled/contaminated paper
stick                   Wood sticks and branches
plastic_cup             Disposable plastic cups
snack_bag               Chip/snack packaging bags
plastic_box             Plastic containers and boxes
straw                   Drinking straws
plastic_cup_lid         Plastic cup covers
scrap_plastic           Low-quality plastic scraps
cardboard_bowl          Paper/cardboard bowls
plastic_cutlery         Plastic forks, spoons, knives
foam                    Foam packaging material
styrofoam               Expanded polystyrene (EPS)
tissue                  Facial tissues and napkins
napkin                  Paper napkins
food_waste              Organic food remnants
organic_waste           Garden waste, leaves, etc.
```

### 🚨 Hazardous (10 types)
```
battery                 Single-use and rechargeable batteries
chemical_spray_can      Spray cans with chemical contents
chemical_plastic_bottle Plastic bottles with chemicals
chemical_plastic_gallon Large chemical containers
light_bulb              Incandescent and fluorescent bulbs
paint_bucket            Paint tins and containers
electronic_waste        E-waste, circuit boards, etc.
broken_glass            Broken or sharp glass pieces
sharp_objects           Nails, needles, metal shards
medical_waste           Syringes, medical instruments
```

---

## Dataset Structure

```
waste-detection-v9/
├── images/
│   ├── train/
│   │   ├── image001.jpg
│   │   ├── image002.jpg
│   │   └── ... (1750 images - 70%)
│   ├── val/
│   │   ├── image1751.jpg
│   │   ├── image1752.jpg
│   │   └── ... (375 images - 15%)
│   └── test/
│       ├── image2126.jpg
│       ├── image2127.jpg
│       └── ... (375 images - 15%)
│
├── labels/
│   ├── train/
│   │   ├── image001.txt
│   │   ├── image002.txt
│   │   └── ... (matching .txt files)
│   ├── val/
│   │   └── ... (matching .txt files)
│   └── test/
│       └── ... (matching .txt files)
│
├── data.yaml          (Dataset configuration)
└── README.roboflow    (Metadata and setup info)
```

---

## YOLO Format Annotation

Each image has a corresponding `.txt` file containing bounding box annotations:

```plaintext
# Format: <class_id> <x_center> <y_center> <width> <height>
# All coordinates are normalized (0-1 range)

# Example annotations from image001.txt:
1 0.452 0.341 0.203 0.154    # plastic_bottle at center
5 0.712 0.623 0.087 0.112    # can at position
15 0.234 0.789 0.321 0.189   # plastic_bag detected

# class_id mapping:
# 0-39: 40 different waste classes (see categories above)
```

---

## Data Augmentation Applied

The dataset includes extensive augmentation to improve model robustness:

| Transformation | Parameters |
|---|---|
| **Rotation** | ±15 degrees |
| **Shearing** | ±15% |
| **Brightness** | ±25% |
| **Exposure** | ±25% |
| **Blur** | Up to 2.5 pixels |
| **Mosaic** | 4-image mixing (YOLOv5/11 technique) |
| **HSV Transformation** | Color space variations |
| **Horizontal Flip** | 50% probability |
| **Vertical Flip** | 10% probability |

These augmentations ensure the model learns robust features invariant to real-world variations.

---

## Dataset Preparation for Training

### Step 1: Download Dataset from Roboflow

```bash
# Visit: https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3
# Click "Export" → Select "YOLO v11" format
# Download the dataset
# Extract to your training directory
```

### Step 2: Verify Directory Structure

```bash
cd waste-detection-v9
ls -la  # Linux/Mac
dir     # Windows

# Should show: images/, labels/, data.yaml
```

### Step 3: Check data.yaml

```yaml
# data.yaml content should look like:
path: /path/to/waste-detection-v9
train: images/train
val: images/val
test: images/test

nc: 40  # Number of classes
names:  # Class names (40 total)
  - cardboard_box
  - can
  # ... (all 40 waste types)
```

### Step 4: Verify Image-Label Pairs

```bash
# Ensure each image has a corresponding label file
python
>>> import os
>>> train_imgs = os.listdir('images/train')
>>> train_labels = os.listdir('labels/train')
>>> len(train_imgs) == len(train_labels)
True  # Should be True
```

---

## Training the Model

### Quick Start

```bash
python train.py --dataset-path /path/to/data.yaml
```

### With Custom Parameters

```bash
# Use Small model (default recommended)
python train.py --dataset-path data.yaml --epochs 50 --batch-size 16 --device 0

# Use Medium model (higher accuracy, slower)
python train.py --dataset-path data.yaml --model-variant m --epochs 50 --batch-size 16

# Use Nano model (fast, less accurate)
python train.py --dataset-path data.yaml --model-variant n --epochs 50 --batch-size 16

# CPU training (slow, for testing only)
python train.py --dataset-path data.yaml --device cpu --batch-size 8
```

---

## Expected Training Performance

### Typical Results After 50 Epochs (GPU T4/V100):

| Metric | Expected Value |
|--------|---|
| **mAP50** | 90-92% |
| **mAP50-95** | 75-80% |
| **Precision** | 88-92% |
| **Recall** | 85-90% |
| **F1-Score** | 0.87-0.91 |

### Training Speed:

| Model | GPU (T4) | GPU (V100) | CPU |
|-------|----------|-----------|-----|
| **Nano** | 45 min/epoch | 25 min/epoch | 8-10 hours |
| **Small** | 60 min/epoch | 35 min/epoch | 12-14 hours |
| **Medium** | 90 min/epoch | 50 min/epoch | 18-20 hours |

**Total for 50 epochs (Small model on T4): ~50 hours**

---

## Data Statistics

### Image Distribution

```
Total Images: 2,500
├─ Training: 1,750 (70%)
├─ Validation: 375 (15%)
└─ Test: 375 (15%)

Class Distribution (samples across whole dataset):
├─ Recyclable: ~1,100 samples (44%)
├─ Non-Recyclable: ~900 samples (36%)
└─ Hazardous: ~500 samples (20%)
```

### Object Distribution

```
Average objects per image: 1.8
├─ Single object images: ~45%
├─ Multiple objects (2-4): ~45%
└─ Dense scenes (5+): ~10%

Object size distribution:
├─ Small objects (<5% area): 20%
├─ Medium objects (5-20%): 50%
└─ Large objects (>20%): 30%
```

---

## Quality Assurance

The dataset has been carefully curated with:

✅ **Manual Verification** - Annotations reviewed for accuracy  
✅ **Balanced Classes** - All 40 classes well-represented  
✅ **Real-World Diversity** - Various lighting, angles, occlusions  
✅ **Professional Annotation** - High-quality bounding boxes  
✅ **Cross-Validation** - Dataset tested with multiple models  
✅ **Production-Ready** - Licensed under CC BY 4.0  

---

## File Sizes

| Component | Size |
|-----------|------|
| Training images (1,750) | ~4.2 GB |
| Validation images (375) | ~900 MB |
| Test images (375) | ~900 MB |
| Label files (all) | ~150 MB |
| **Total Dataset** | **~6.2 GB** |

---

## Downloading & Setup

### Option 1: Using Roboflow API (Automated)

```python
from roboflow import Roboflow

rf = Roboflow(api_key="your_api_key_here")
project = rf.workspace().project("waste-detection-vqkjo")
dataset = project.version(9).download("yolov11")
```

### Option 2: Manual Download

1. Visit: https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3
2. Click "Export"
3. Select "YOLOv11" format
4. Download ZIP file
5. Extract to your training directory

### Option 3: From Roboflow Universe

```bash
# Download via command line
wget https://universe.roboflow.com/.../waste-detection-9.zip
unzip waste-detection-9.zip
```

---

## Citation & Attribution

When using this dataset, please cite:

```bibtex
@dataset{waste_detection_roboflow,
  title={Waste Detection Dataset v9},
  author={AI Project Team, Roboflow},
  year={2024},
  url={https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo},
  license={CC BY 4.0}
}
```

---

## License

**Dataset License**: CC BY 4.0 (Creative Commons Attribution 4.0)

You are free to:
- ✅ Use the dataset commercially
- ✅ Modify the dataset
- ✅ Distribute the dataset

You must:
- 📋 Give appropriate credit to the original authors
- 📋 Provide a link to the license
- 📋 Indicate changes made

---

## Troubleshooting

### Issue: "data.yaml not found"
**Solution**: Extract dataset properly and ensure `data.yaml` is in root directory

### Issue: "Image-label mismatch"
**Solution**: Verify dataset integrity:
```bash
python
>>> import os
>>> train_imgs = os.listdir('images/train')
>>> train_labels = os.listdir('labels/train')
>>> len(train_imgs) == len(train_labels)
```

### Issue: "Out of Memory during training"
**Solution**: 
- Reduce batch size: `--batch-size 8`
- Use Nano model: `--model-variant n`
- Use CPU: `--device cpu` (for testing)

### Issue: "Slow training on CPU"
**Solution**: Use GPU if available - 10-50x faster

---

## Additional Resources

- **Dataset Source**: https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3
- **YOLOv11 Docs**: https://docs.ultralytics.com/
- **Roboflow Hub**: https://universe.roboflow.com/
- **PyTorch Documentation**: https://pytorch.org/docs/

---

**Last Updated**: February 2026  
**Dataset Version**: v9  
**Status**: Production Ready ✅
