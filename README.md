# ♻️ Intelligent Waste Segregation System

AI-powered real-time waste detection using **YOLOv11** (92% mAP50) and **Google Gemini 2.0 Flash** for recycling recommendations. Classifies waste into recyclable, non-recyclable, and hazardous categories with 90%+ accuracy.

## 🚀 Quick Start

```bash
git clone https://github.com/boss4848/waste-detection.git
cd waste-detection
pip install -r requirements.txt
streamlit run app.py
```

**Requirements**: Python 3.8+, Webcam, [Gemini API Key](https://makersuite.google.com/app/apikey) (free)

## ✨ Features

- **Real-time Detection** (30 FPS on GPU, 10 FPS on CPU)
- **3 Model Options**: Nano (fast), Small (balanced), Medium (accurate)
- **AI Recommendations** via Gemini 2.0 Flash
- **Auto Logging** with analytics dashboard
- **GPU Accelerated** (CUDA support)

## 🛠️ Tech Stack

| Tech | Why |
|------|-----|
| **YOLOv11** | Best-in-class object detection (92% mAP50, real-time inference) |
| **PyTorch 2.6** | GPU acceleration + industry standard |
| **Streamlit** | Fast web UI with real-time updates |
| **Gemini 2.0 Flash** | Fast, cost-effective AI recommendations |
| **OpenCV** | Efficient video processing |

## 📊 Dataset & Model

**Dataset**: [Roboflow Waste Detection v9](https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3) (CC BY 4.0)
- 2,500+ images, 40+ waste classes, 70/15/15 split
- Trained 50 epochs on Google Colab (Tesla T4/V100)

**Performance**: mAP50: 92% | Precision: 90% | Recall: 88%

**Models**:
- Nano (2.6M params): 5ms inference - for real-time speed
- Small (9.6M params): 10ms inference - balanced
- Medium (20.1M params): 15ms inference - maximum accuracy

## 📁 Structure

```
waste-detection/
├── app.py              # Streamlit UI + analytics dashboard
├── helper.py           # YOLOv11 detection + Gemini AI + logging
├── settings.py         # Config & 40+ waste categories
├── train.py            # Custom model training
├── weights/best.pt     # Fine-tuned model
├── detection_logs.json # Auto-generated session logs
└── detection_stats.csv # Auto-generated statistics
```

*See `structure.txt` for complete technical details*

## 📈 Visualizations

All detection data is logged and visualized in the Streamlit app:
- **Detection History**: Recent sessions with timestamps & metrics
- **Analytics Dashboard**: Category distribution, top items, timeline charts
- **Statistics Table**: Item frequencies and confidence scores

Enable via **"📈 Show Analytics Dashboard"** in sidebar

## 🎓 Training

```bash
python train.py  # Update dataset path in file
```

## 🌐 Live Demo

[intelligent-waste-segregation-system.streamlit.app](https://intelligent-waste-segregation-system.streamlit.app)

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| No webcam | Check permissions, change index in `settings.py` |
| No GPU | Install CUDA 11.8+, verify: `python -c "import torch; print(torch.cuda.is_available())"` |
| API error | Get valid key at [Google AI Studio](https://makersuite.google.com/app/apikey) |

## 📚 Resources

[Dataset](https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3) • [Training Notebook](https://colab.research.google.com/drive/1dHv5QUuz2NkkgzeKBoO4DLAhLg9mOrzv) • [YOLOv11 Docs](https://docs.ultralytics.com/) • [Streamlit Docs](https://docs.streamlit.io/)

---

**MIT License** | **v2.0** | Production Ready ✅
