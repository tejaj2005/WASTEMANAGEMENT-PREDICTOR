# 📦 Dataset & Training Guide — AI E-Waste Detection System

> **Target:** 95–99% mAP@50 · 100 classes · YOLOv8x / YOLOv9x · 50K–100K images

---

## 📋 Quick Reference

| Parameter | Value |
|-----------|-------|
| **Total Classes** | 100 |
| **Categories** | 10 |
| **Images per Class** | 500–1,200 |
| **Total Images** | 50,000–100,000 |
| **Image Size** | 640×640 px |
| **Train / Val / Test** | 70% / 20% / 10% |
| **Model** | YOLOv8x (or YOLOv9x) |
| **Target mAP@50** | ≥ 95% |

---

## 🗂️ Full Class List (100 Classes)

### Category 1 — 📱 Mobile Devices (IDs 0–9)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 0 | Smartphone | Conflict minerals (Ta, Co) — specialist recycler |
| 1 | Feature Phone | Low hazard — municipal e-waste bin |
| 2 | Tablet | Li-Po battery — must discharge before disposal |
| 3 | Smartwatch | Tiny Li-ion — WEEE drop-off point |
| 4 | Fitness Band | Small battery — avoid landfill |
| 5 | Mobile Battery | ⚠️ Lithium fire risk — dedicated battery recycler |
| 6 | Mobile Back Cover | Aluminium/plastic — general e-waste |
| 7 | Mobile Screen | Contains indium — specialist recycler |
| 8 | Mobile Motherboard | 🚨 PCB lead/cadmium — precious metal recovery |
| 9 | SIM Card Tray | Aluminium — general metal recycling |

### Category 2 — 💻 Computing Devices (IDs 10–19)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 10 | Laptop | Data wipe first — WEEE certified recycler |
| 11 | Desktop Computer | Remove HDD first — metal frame recyclable |
| 12 | Monitor | LCD: mercury-free. CRT: hazardous |
| 13 | All-in-One Computer | Integrated display — specialist handling |
| 14 | Mini PC | Small form factor — standard e-waste |
| 15 | Server Unit | Data destruction mandatory — certified recycler |
| 16 | Thin Client | Low hazard — standard IT recycler |
| 17 | Computer Cabinet | Steel/aluminium — metal recycler |
| 18 | Laptop Charger | Copper windings — cable recycler |
| 19 | Laptop Cooling Pad | Mixed plastic/metal — standard e-waste |

### Category 3 — ⌨️ Computer Peripherals (IDs 20–29)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 20 | Keyboard | Plastic/copper — standard e-waste |
| 21 | Mouse | Small plastic — standard e-waste |
| 22 | Gaming Mouse | RGB LEDs — standard e-waste |
| 23 | Mechanical Keyboard | Hall-effect switches — standard e-waste |
| 24 | Webcam | Small lens — standard e-waste |
| 25 | Microphone | Mixed materials — standard e-waste |
| 26 | Computer Speaker | Magnet recovery — standard e-waste |
| 27 | External Webcam | USB device — standard e-waste |
| 28 | Graphics Tablet | Contains digitizer — standard e-waste |
| 29 | Barcode Scanner | Laser/LED — standard e-waste |

### Category 4 — 💾 Storage Devices (IDs 30–39)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 30 | Hard Disk Drive | ⚠️ Data wipe / physical destruction required |
| 31 | Solid State Drive | ⚠️ Data destruction — NAND flash specialist |
| 32 | External Hard Disk | Data wipe then e-waste recycler |
| 33 | USB Flash Drive | Small — e-waste drop-off |
| 34 | Memory Card | Tiny — e-waste collection point |
| 35 | Micro SD Card | Very small — collect in batch |
| 36 | CD Disk | Polycarbonate — optical media recycler |
| 37 | DVD Disk | Polycarbonate + aluminium — optical media recycler |
| 38 | Floppy Disk | Legacy — specialist media recycler |
| 39 | NAS Storage Unit | Multiple HDDs — data destroy + e-waste |

### Category 5 — 🔧 Computer Components (IDs 40–49)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 40 | Motherboard | 🚨 PCB: lead/cadmium — precious metal (Au/Ag) recovery |
| 41 | CPU Processor | 🚨 Gold pins — precious metal smelter |
| 42 | GPU | 🚨 VRAM: rare earth — specialist recycler |
| 43 | RAM Module | PCB + gold pins — precious metal recovery |
| 44 | Power Supply Unit | Copper transformer — WEEE recycler |
| 45 | Cooling Fan | Plastic/metal — standard e-waste |
| 46 | Heat Sink | Aluminium/copper — metal recycler |
| 47 | CMOS Battery | ⚠️ CR2032 lithium — battery recycler |
| 48 | Expansion Card | PCB — precious metal recovery |
| 49 | Network Card | PCB — e-waste recycler |

### Category 6 — ⚡ Circuit Components (IDs 50–59)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 50 | PCB Board | 🚨 Lead solder — hydrometallurgical recovery |
| 51 | Integrated Circuit | 🚨 Rare earth dopants — specialist smelter |
| 52 | Capacitor | Electrolytic: acid — chemical disposal |
| 53 | Resistor | Low hazard — PCB recycler |
| 54 | Transistor | Silicon/germanium — semiconductor recycler |
| 55 | Inductor | Ferrite core + copper — PCB recycler |
| 56 | Diode | Silicon — semiconductor recycler |
| 57 | Voltage Regulator | PCB-mounted — e-waste |
| 58 | Crystal Oscillator | Quartz — specialist recycler |
| 59 | Relay | Contacts may contain silver — PCB recycler |

### Category 7 — 🖥️ Display Devices (IDs 60–69)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 60 | LCD Panel | 🚨 CCFL backlight: mercury — hazardous waste |
| 61 | LED Panel | Low hazard — standard e-waste |
| 62 | CRT Monitor | 🚨 Lead glass (2–8 kg) — specialist CRT recycler only |
| 63 | Television | LCD: standard. CRT: specialist required |
| 64 | Smart TV | Android board + display — IT recycler |
| 65 | Projector | Lamp: mercury — specialist recycler |
| 66 | Projector Lens | Glass — optical waste |
| 67 | Display Controller Board | PCB — e-waste |
| 68 | TV Remote | Batteries first, then e-waste |
| 69 | LED Driver Board | PCB — e-waste |

### Category 8 — 🎵 Audio Devices (IDs 70–79)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 70 | Headphones | Mixed: magnets + plastic + copper |
| 71 | Earphones | Small — e-waste collection |
| 72 | Bluetooth Headset | Lithium rechargeable — battery removal first |
| 73 | Wireless Earbuds | ⚠️ Tiny Li-Po — battery specialist |
| 74 | Soundbar | Speaker magnets recoverable |
| 75 | Subwoofer | Heavy magnet — metal recycler |
| 76 | Amplifier | Transformer copper — e-waste |
| 77 | Audio Receiver | Mixed electronics — e-waste |
| 78 | Microphone | Small — standard e-waste |
| 79 | DJ Controller | Large PCB — e-waste |

### Category 9 — 📡 Networking Devices (IDs 80–89)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 80 | WiFi Router | Antenna: aluminium — standard e-waste |
| 81 | Network Switch | Rack-mount metal — e-waste |
| 82 | Modem | Standard e-waste |
| 83 | LAN Cable | Copper — cable recycler |
| 84 | Ethernet Connector | Small — bulk e-waste |
| 85 | Network Antenna | Aluminium/copper — metal recycler |
| 86 | Access Point | Compact — standard e-waste |
| 87 | Signal Booster | Standard e-waste |
| 88 | Fiber Converter | Optical + electronics — e-waste |
| 89 | Network Hub | Legacy — standard e-waste |

### Category 10 — 🔋 Power Devices (IDs 90–99)
| ID | Class Name | Key Recycling Note |
|----|------------|--------------------|
| 90 | Battery | 🚨 Acid — dedicated battery collection |
| 91 | Lithium Battery | 🚨 Fire risk — NEVER standard bin — battery retailer |
| 92 | Power Adapter | Transformer copper — e-waste |
| 93 | Charger | USB/wireless — e-waste |
| 94 | UPS | 🚨 Lead-acid battery — battery specialist |
| 95 | Inverter | Lead-acid + PCB — specialist |
| 96 | Power Bank | 🚨 Lithium cells — battery recycler |
| 97 | Extension Board | Copper + plastic — e-waste |
| 98 | Power Cable | Copper — cable recycler |
| 99 | Adapter Plug | Small — e-waste |

---

## 📁 Required Dataset Structure

```
dataset/
├── images/
│   ├── train/          ← 70%  ~35,000–70,000 images
│   │   ├── img_0001.jpg
│   │   └── ...
│   ├── val/            ← 20%  ~10,000–20,000 images
│   └── test/           ← 10%  ~5,000–10,000 images
└── labels/
    ├── train/          ← matching .txt annotations
    │   ├── img_0001.txt
    │   └── ...
    ├── val/
    └── test/
```

Each `.txt` annotation file (one row per object):
```
<class_id> <x_center> <y_center> <width> <height>
```
All values are **normalized 0.0–1.0**. Example:
```
42  0.512 0.388 0.245 0.312    ← GPU at center-right, 25%×31% of frame
0   0.123 0.750 0.180 0.220    ← Smartphone bottom-left
```

---

## 🌐 Dataset Sources

### Option A — Roboflow (Recommended)
```
https://universe.roboflow.com/
```
Search terms:
- `"e-waste detection"`
- `"electronic components"`
- `"PCB detection"`
- `"mobile phones detection"`
- `"circuit board"`

Download in **YOLOv8 format** — files drop directly into `dataset/`.

### Option B — Open Images V7
```
https://storage.googleapis.com/openimages/web/index.html
```
Use `fiftyone` to download specific classes:
```python
import fiftyone.zoo as foz
dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="train",
    label_types=["detections"],
    classes=["Laptop", "Mobile phone", "Television", "Keyboard", "Mouse",
             "Headphones", "Router", "Hard drive"],
    max_samples=5000,
)
```

### Option C — COCO Dataset
```
https://cocodataset.org/
```
Useful classes: laptop, cell phone, tv, keyboard, mouse, remote

### Option D — Web Scraping + Manual Annotation
1. Collect images with tools like `icrawler`:
```python
from icrawler.builtin import GoogleImageCrawler
crawler = GoogleImageCrawler(storage={"root_dir": "raw_images/smartphone"})
crawler.crawl(keyword="smartphone e-waste recycling", max_num=1000)
```
2. Annotate with **Roboflow Annotate** (free) or **CVAT** (open-source)

---

## 🔧 Training Commands

```bash
# 1. Generate data.yaml
python train.py generate-yaml

# 2. Validate your dataset structure
python train.py validate-dataset

# 3. Check per-class counts (find imbalanced classes)
python train.py stats

# 4. Dry run (validate config, don't train)
python train.py train --dry-run

# 5. Full training run
python train.py train --epochs 300 --batch 16 --model yolov8x.pt

# 6. Resume from checkpoint (after interruption)
python train.py train --resume

# 7. Validate on test set
python train.py validate --model weights/best.pt

# 8. Export to ONNX for deployment
python train.py export --format onnx
```

---

## ⚙️ Training Configuration (Spec)

```yaml
Model:        YOLOv8x (largest, most accurate)
Epochs:       200–300
Batch Size:   16–32  (adjust for VRAM: 8GB→8, 16GB→16, 24GB→32)
Image Size:   640×640
Learning Rate: 0.001 (cosine decay)
Optimizer:    AdamW
Patience:     50 epochs (early stop)
```

### GPU VRAM Guide
| GPU | VRAM | Recommended Batch |
|-----|------|-------------------|
| RTX 3060 | 12 GB | 16 |
| RTX 3080 | 10 GB | 12 |
| RTX 3090 | 24 GB | 32 |
| RTX 4090 | 24 GB | 32 |
| A100 | 40/80 GB | 64 |
| Google Colab T4 | 16 GB | 16 |
| Google Colab A100 | 40 GB | 32 |

### Google Colab Setup (Free GPU)
```python
# In Colab notebook:
!pip install ultralytics
from google.colab import drive
drive.mount('/content/drive')

# Upload dataset to Drive, then:
!python train.py train --epochs 300 --batch 16 --device 0
```

---

## 📊 Data Augmentation (Applied Automatically)

| Augmentation | Value | Effect |
|-------------|-------|--------|
| Rotation | ±10° | Handle tilted items |
| Translation | ±10% | Handle off-center items |
| Scale | ±50% | Handle different distances |
| Horizontal Flip | 50% | Mirror images |
| Vertical Flip | 10% | Rare but useful |
| Mosaic | 100% | Combine 4 images (key for small objects) |
| MixUp | 15% | Blend two images |
| Copy-Paste | 10% | Copy objects to new backgrounds |
| HSV Hue | ±1.5% | Color variation |
| HSV Saturation | ±70% | Color variation |
| HSV Value | ±40% | Brightness/darkness |
| Random Erasing | 40% | Handle partial occlusion |

---

## 🎯 Expected Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| mAP@50 | ≥ 95% | Primary metric |
| mAP@50-95 | ≥ 80% | Strict metric |
| Precision | > 92% | Low false positives |
| Recall | > 92% | Low false negatives |
| FPS (GPU) | 30+ | Real-time capable |
| FPS (CPU) | 5–10 | Inference only |

### Reaching 95%+ Tips
1. **Minimum 800 images per class** — aim for 1,000+
2. **Diverse backgrounds** — cluttered desks, outdoors, bins, warehouses
3. **Multiple angles** — top-down, 45°, side view, close-up
4. **Multiple lighting** — bright, dim, fluorescent, natural
5. **Occluded examples** — partially hidden items
6. **Scale variation** — item takes 5% to 90% of frame area
7. **Use mosaic augmentation** — enabled by default in our config

---

## 🧹 Image Preprocessing

Our training pipeline applies automatically:
- **Resize** to 640×640 (letterbox with padding)
- **Normalize** pixel values 0–1
- **Remove noise** (handled by augmentation)
- **Balance dataset** — oversample underrepresented classes

Manual preprocessing (before training):
```python
# Check and remove corrupt images
from PIL import Image
from pathlib import Path

for img_path in Path("dataset/images").rglob("*.jpg"):
    try:
        Image.open(img_path).verify()
    except Exception:
        print(f"Removing corrupt: {img_path}")
        img_path.unlink()
```

---

## 📈 Monitoring Training

Training logs are saved to `runs/ewaste/`. Open TensorBoard:
```bash
tensorboard --logdir runs/ewaste
```

Key metrics to watch:
- `train/box_loss` — bounding box accuracy (should decrease)
- `val/mAP50` — validation accuracy (should increase to ≥0.95)
- `val/mAP50-95` — strict accuracy (aim ≥0.80)
- `lr/pg0` — learning rate (cosine decay from 0.001)

---

## 🚀 Deployment After Training

```bash
# Test on webcam
python app.py   # uses weights/best.pt automatically

# Export for edge devices
python train.py export --format tflite     # Mobile (TensorFlow Lite)
python train.py export --format onnx       # Universal (ONNX Runtime)
python train.py export --format engine     # NVIDIA TensorRT (fastest GPU)
python train.py export --format coreml     # Apple devices
```

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| Roboflow Dataset Search | [universe.roboflow.com](https://universe.roboflow.com/) |
| YOLOv8 Docs | [docs.ultralytics.com](https://docs.ultralytics.com/) |
| CVAT Annotation Tool | [cvat.ai](https://cvat.ai/) |
| Google Colab (free GPU) | [colab.research.google.com](https://colab.research.google.com/) |
| Open Images V7 | [storage.googleapis.com/openimages](https://storage.googleapis.com/openimages/web/index.html) |
| FiftyOne (dataset tools) | [voxel51.com/fiftyone](https://voxel51.com/fiftyone/) |
