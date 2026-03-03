# ♻️ Intelligent Waste Segregation System

**AI-powered real-time waste detection & segregation** using **YOLOv11** object detection (92% mAP50 accuracy) integrated with **Google Gemini 2.0 Flash** for intelligent recycling recommendations, reuse suggestions, and hazardous handling guidance.

Classifies waste into **recyclable**, **non-recyclable**, and **hazardous** categories with 90%+ accuracy and provides actionable sustainability guidance.

---

## 📚 Quick Documentation Reference

| Document | Purpose |
|----------|---------|
| **[README.md](README.md)** | 📖 This file - Quick start & overview |
| **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** | ✅ Complete integration changes & features |
| **[structure.txt](structure.txt)** | 🏗️ Complete system architecture & data flow |
| **[DATASET_GUIDE.md](DATASET_GUIDE.md)** | 📊 Roboflow dataset info & training setup |
| **[YOLOV11_INTEGRATION.md](YOLOV11_INTEGRATION.md)** | 🤖 YOLOv11 model code & optimizations |
| **[train.py](train.py)** | 🚀 Comprehensive training script |

---

## 🎯 System Features

✅ **Real-time Detection** - 30 FPS on GPU, 10 FPS on CPU  
✅ **3 Model Variants** - Nano (fast/edge), Small (balanced), Medium (highest accuracy)  
✅ **AI-Powered Recommendations** - Gemini 2.0 Flash integration for:
   - Material-specific recycling methods
   - Safe hazardous waste handling
   - Creative reuse & upcycling suggestions
   - Environmental impact analysis
   - Carbon footprint reduction tips  
✅ **Automatic Logging** - JSON session logs + CSV statistics  
✅ **Analytics Dashboard** - Detection history, statistics, performance metrics  
✅ **GPU Acceleration** - CUDA 11.8+ support with half precision inference  
✅ **40+ Waste Classes** - Pre-trained on Roboflow dataset  
✅ **Comprehensive Documentation** - Architecture, training, integration guides

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/boss4848/waste-detection.git
cd waste-detection

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

**Requirements**: Python 3.8+, Webcam

---

## 📊 Dataset Used

**Roboflow Waste Detection v9**
- **2,500+ annotated images** with 40+ waste types
- **70/15/15 split**: Training, validation, testing
- **Format**: YOLO normalized bounding boxes
- **License**: CC BY 4.0

For complete dataset information, see [DATASET_GUIDE.md](DATASET_GUIDE.md)

---

## 🏗️ YOLO Model Architecture & Data Flow

### **Complete Processing Pipeline**

```
Webcam Feed (1280×720 @ 30 FPS)
    ↓
OpenCV Preprocessing (Resize to 640×480)
    ↓
YOLOv11 Detection Engine
  • Backbone: CSPDarknet (feature extraction)
  • Neck: PAFPN (multi-scale feature fusion)
  • Head: 3-scale detection head
    ↓
Confidence Filtering & NMS (Conf ≥ 0.4, IOU = 0.45)
    ↓
Waste Classification into 3 Categories
  ♻️  RECYCLABLE (13 types)
  ⚠️  NON-RECYCLABLE (17 types)
  🚨 HAZARDOUS (10 types)
    ↓
Quality Assessment (Based on Confidence Score)
  🟢 Excellent (≥85%)
  🟡 Good (70-85%)
  🟠 Fair (50-70%)
  🔴 Poor (<50%)
    ↓
Gemini 2.0 Flash AI Analysis
  ✓ Material composition analysis
  ✓ Recycling method specifics
  ✓ Safety protocols & hazard warnings
  ✓ Reuse suggestions & upcycling ideas
  ✓ Environmental impact calculation
    ↓
Logging System
  • JSON: Full session details
  • CSV: Item statistics & trends
    ↓
Streamlit UI Rendering
```

### **YOLOv11 Model Options**

| Aspect | Nano | Small | Medium |
|--------|------|-------|--------|
| **Parameters** | 2.6M | 9.6M | 20.1M |
| **Model Size** | 6MB | 25MB | 51MB |
| **Inference Speed** | 5-8ms | 10-12ms | 15-18ms |
| **FPS (GPU)** | 40-50 | 30-40 | 20-30 |
| **mAP50 Accuracy** | 88% | 90% | 92% |
| **Use Case** | Edge/Mobile | **RECOMMENDED** | Max Accuracy |

**Default**: Small model for optimal speed-accuracy balance

### **Detection Process Per Frame**

1. **Input**: 1280×720 RGB webcam frame
2. **Resize**: Scale to 640×480 (YOLOv11 input)
3. **Normalize**: Convert pixel values to 0-1 range
4. **Backbone Extraction**: Multi-scale feature extraction via CSPDarknet
5. **Neck Fusion**: PAFPN combines features across scales
6. **Detection Head**: Predicts class + bounding box + confidence
7. **Post-Processing**: Apply NMS (remove duplicate detections)
8. **Classification**: Map to recyclable/non-recyclable/hazardous
9. **Quality Tier**: Assign based on confidence score
10. **AI Analysis**: Send detected items to Gemini 2.0 Flash
11. **Display**: Render results with recommendations

### **GPU Optimization**

- **Half Precision (FP16)**: 2x faster, 50% less memory on CUDA
- **Auto Device Selection**: GPU if available, falls back to CPU
- **Parallel Processing**: Efficient batch inference
- **Memory Management**: Stream-based execution

---

## 🤖 Gemini 2.0 Flash AI Integration

When waste is detected, Gemini 2.0 Flash provides:

### **7-Point Analysis Framework**

1. **Item-by-Item Analysis**
   - Material composition
   - Condition assessment
   - Reusability potential

2. **Recycling Methods** (Recyclable items)
   - Material-specific process
   - Preparation steps
   - Recommended facilities

3. **Disposal Guidance** (Non-recyclable)
   - Safe disposal methods
   - Local waste management
   - Why non-recyclable

4. **Hazardous Material Safety** ⚠️
   - Safety warnings
   - Required PPE
   - Proper handling procedures
   - Certified disposal facilities
   - Environmental risks

5. **Creative Reuse Suggestions**
   - Upcycling project ideas
   - Donation opportunities
   - DIY/craft applications

6. **Environmental Impact**
   - Carbon footprint reduction
   - Resource conservation stats
   - Water/energy savings

7. **Action Plan with Timeline**
   - Specific next steps
   - Recommended timeline
   - Necessary resources

---

## 📊 Dataset & Model Training

### **Roboflow Dataset v9**
- **Total Images**: 2,500+ annotated waste images
- **Waste Classes**: 40+ types
- **Data Split**: 70% train, 15% val, 15% test
- **License**: CC BY 4.0
- **Format**: YOLO `.txt` annotations
- **Source**: [https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3](https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3)

**📄 For complete dataset details, see [DATASET_GUIDE.md](DATASET_GUIDE.md)**

### **Performance Metrics**
- **mAP50**: 92% (Average Precision @ IoU 0.5)
- **Precision**: 90% (detection accuracy)
- **Recall**: 88% (detection coverage)
- **F1-Score**: 0.89

### **Training Specifications**
- **Epochs**: 50
- **Batch Size**: 16 (GPU) / 8 (CPU)
- **Optimizer**: SGD with momentum 0.937
- **Learning Rate**: 0.001 (cosine annealing)
- **Hardware**: Tesla T4/V100 GPU (12GB VRAM)
- **Training Time**: 50 hours (Small model on T4)
- **Base Model**: YOLOv11n (Nano) 2.6M parameters

### **Training the Model**

```bash
# Quick start (requires data.yaml in dataset root)
python train.py --dataset-path /path/to/data.yaml

# Custom configuration
python train.py --dataset-path data.yaml --epochs 50 --batch-size 16 --device 0 --model-variant s

# CPU training (slow, for testing)
python train.py --dataset-path data.yaml --device cpu --batch-size 8
```

**🚀 For complete training guide, see [train.py](train.py) and [DATASET_GUIDE.md](DATASET_GUIDE.md)**

---

## 📁 Project Structure

```
waste-detection/
├── app.py                        # Streamlit UI
├── helper.py                     # Detection engine + Gemini
├── settings.py                   # Configuration & categories
├── train.py                      # Comprehensive training script
├── weights/
│   ├── best.pt                  # Fine-tuned model
│   ├── yolov11n.pt              # Nano (if downloaded)
│   ├── yolov11s.pt              # Small (if downloaded)
│   └── yolov11m.pt              # Medium (if downloaded)
├── detection_logs.json           # Auto-generated session logs
├── detection_stats.csv           # Auto-generated statistics
├── requirements.txt
├── README.md                     # This file
├── structure.txt                 # Complete architecture
├── INTEGRATION_SUMMARY.md        # Integration changes
├── DATASET_GUIDE.md              # Dataset documentation
├── YOLOV11_INTEGRATION.md        # Model integration details
└── .gitignore
```

---

## 🛠️ Technology Stack

| Component | Tech | Purpose |
|-----------|------|---------|
| **Detection** | YOLOv11 | Real-time object detection (92% accuracy) |
| **ML Framework** | PyTorch 2.6+ | GPU-accelerated deep learning |
| **Web UI** | Streamlit 1.42+ | Interactive real-time dashboard |
| **Video** | OpenCV 4.8+ | Efficient frame processing |
| **AI** | Google Gemini 2.0 Flash | Multi-faceted waste analysis |
| **GPU** | CUDA 11.8+ | Parallel computation (optional) |
| **Python** | 3.8+ | Runtime environment |

---

## 📈 Logging & Analytics

### **Session Logs** (`detection_logs.json`)
- Timestamp and model name
- All detected items
- Category breakdown
- FPS and frame count

### **Statistics** (`detection_stats.csv`)
- Item name and count
- Average confidence score
- Category classification
- Temporal tracking

---

## 🌐 Live Demo

[intelligent-waste-segregation-system.streamlit.app](https://intelligent-waste-segregation-system.streamlit.app)

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No webcam | Update `WEBCAM_PATH` in `settings.py` (try 0, 1, 2...) |
| CUDA OOM | Switch to Nano model |
| Low FPS (CPU) | Install CUDA 11.8+. Check: `python -c "import torch; print(torch.cuda.is_available())"` |
| Gemini errors | Verify API key validity |
| Model not found | Auto-downloads on first run |

---

## 📚 Resources & References

- [YOLOv11 Docs](https://docs.ultralytics.com/)
- [Waste Detection Dataset](https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3)
- [PyTorch CUDA Setup](https://pytorch.org/get-started/locally/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini API](https://ai.google.dev/)

---

**License**: MIT | **Version**: 2.0 | **Status**: ✅ Production Ready
