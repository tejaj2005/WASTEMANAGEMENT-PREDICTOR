# ♻️ Intelligent Waste Segregation System

**AI-powered real-time waste detection & segregation** using **YOLO11** for object detection (92% mAP50) and **Google Gemini 2.0 Flash** for intelligent recycling recommendations.

Classifies waste into **Recyclable**, **Non-Recyclable**, and **Hazardous** categories with 90%+ accuracy.

---

## 🎯 Features

- **Real-time detection** — 30 FPS on GPU, 10 FPS on CPU
- **3 model variants** — Nano (fast), Small (balanced), Medium (accurate)
- **AI recycling guidance** — material-specific methods, hazard warnings, reuse tips via Gemini 2.0 Flash
- **40+ waste classes** — trained on Roboflow Waste Detection v9
- **Analytics dashboard** — session history, statistics, performance metrics
- **Automatic logging** — JSON session logs + CSV item statistics
- **GPU acceleration** — CUDA FP16 half-precision inference

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/tejaj2005/WASTEMANAGEMENT-PREDICTOR.git
cd WASTEMANAGEMENT-PREDICTOR

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API key
#    Copy .env.example to .env and paste your key
#    Get a free key → https://aistudio.google.com/app/apikey
cp .env.example .env

# 4. Run
streamlit run app.py
```

**Requirements:** Python 3.8+, Webcam

---

## 📁 Project Structure

```
├── app.py              # Streamlit UI (frontend)
├── helper.py           # Detection engine + Gemini AI integration
├── settings.py         # Configuration (paths, categories, API keys)
├── requirements.txt    # Python dependencies
├── packages.txt        # System packages (for Streamlit Cloud)
├── .env.example        # API key template
├── .env                # Your API keys (gitignored)
├── .gitignore
├── .streamlit/
│   └── config.toml     # Streamlit settings
├── weights/
│   └── best.pt         # Custom-trained YOLO model
├── structure.txt       # Detailed architecture documentation
├── API_SETUP_GUIDE.md  # Step-by-step Gemini API setup
├── DATASET_GUIDE.md    # Dataset info & training instructions
└── README.md           # This file
```

---

## 🏗️ Architecture

```
Webcam (1280×720 @ 30 FPS)
    ↓
OpenCV Preprocessing (resize → 640×480)
    ↓
YOLO11 Detection Engine
  • Backbone: CSPDarknet
  • Neck: PAFPN (multi-scale fusion)
  • Head: 3-scale detection
    ↓
Post-processing (confidence ≥ 0.4, NMS IoU = 0.45)
    ↓
Waste Classification
  ♻️  Recyclable (13+ types)
  ⚠️  Non-Recyclable (17 types)
  🚨 Hazardous (10 types)
    ↓
Quality Assessment (🟢 Excellent → 🔴 Poor)
    ↓
Gemini 2.0 Flash AI Analysis
  • Recycling methods
  • Hazard warnings
  • Environmental impact
    ↓
Streamlit UI + Logging
```

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| **mAP50** | 92% |
| **Precision** | 90% |
| **Recall** | 88% |
| **F1-Score** | 0.89 |

### Model Variants

| Model | Params | Size | Speed (GPU) | Accuracy |
|-------|--------|------|-------------|----------|
| Nano | 2.6M | 6 MB | 5–8 ms | 88% |
| Small | 9.6M | 25 MB | 10–12 ms | 90% |
| Medium | 20.1M | 51 MB | 15–18 ms | 92% |

---

## 📊 Dataset

**Roboflow Waste Detection v9**
- 2,500+ annotated images, 40+ waste classes
- 70/15/15 train/val/test split
- YOLO format annotations
- [Dataset link](https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3)

For details see [DATASET_GUIDE.md](DATASET_GUIDE.md).

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Detection | YOLO11 (Ultralytics) |
| ML Framework | PyTorch 2.6+ |
| Web UI | Streamlit 1.42+ |
| Video | OpenCV 4.8+ |
| AI Analysis | Google Gemini 2.0 Flash |
| GPU | CUDA 11.8+ (optional) |

---

## 🔑 API Configuration

The only API key you need is a **Google Gemini key** (free tier available):

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Create a key (starts with `AIza…`)
3. Paste it into your `.env` file or the sidebar input in the app

See [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) for a detailed walkthrough.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No webcam | Change `WEBCAM_INDEX` in `settings.py` (try 0, 1, 2) |
| CUDA OOM | Switch to Nano model |
| Low FPS | Install CUDA 11.8+ or use Nano model |
| Gemini errors | Check API key & internet connection |
| Model not found | Ensure `weights/best.pt` exists |

---

## 📚 Resources

- [YOLO11 Docs](https://docs.ultralytics.com/)
- [Roboflow Dataset](https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3)
- [PyTorch CUDA Setup](https://pytorch.org/get-started/locally/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Google Gemini API](https://ai.google.dev/)

---

**License:** MIT  ·  **Version:** 2.0  ·  **Status:** ✅ Production Ready
