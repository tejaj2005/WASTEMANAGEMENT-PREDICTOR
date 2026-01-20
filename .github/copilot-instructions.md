# AI Agent Instructions: Waste Detection System

## Project Overview
This is a real-time waste detection and segregation system using **YOLOv11** for object detection and **Google Gemini 2.0 Flash** for AI-powered recycling recommendations. The application runs as a Streamlit web UI that processes webcam video streams.

**Key Goal**: Classify waste into recyclable, non-recyclable, and hazardous categories with 90%+ accuracy and provide actionable recycling guidance.

---

## Architecture & Data Flow

### Core Components
1. **app.py** (Streamlit UI Layer)
   - Model selection (Nano/Small/Medium YOLOv11 variants)
   - Webcam stream handling
   - Real-time detection UI with confidence threshold slider
   - Analytics dashboard (detection history & statistics)

2. **helper.py** (Detection & Processing Engine)
   - `load_model()`: Loads YOLOv11 with GPU/CPU optimization (half precision for CUDA)
   - `run_detection()`: Processes frames, returns bounding boxes with confidence scores
   - `classify_waste_type()`: Maps detected items to waste categories from settings
   - Logging: Persists sessions as JSON, item stats as CSV
   - Gemini integration: Generates recycling recommendations from detected items

3. **settings.py** (Configuration & Categories)
   - **40+ waste classes** split into 3 categories:
     - `RECYCLABLE`: cardboard, cans, glass, paper, plastic bottles, etc.
     - `NON_RECYCLABLE`: plastic bags, foam, tissue, styrofoam, etc.
     - `HAZARDOUS`: batteries, bulbs, e-waste, sharp objects, chemicals, etc.
   - `WEBCAM_PATH`: Index of webcam device (default: 0)
   - `MODEL_DIR`: Path to weights folder (best.pt, yolov11n/s/m.pt)

4. **Model Weights**
   - `weights/best.pt`: Fine-tuned model (trained 50 epochs on Roboflow dataset v9)
   - Auto-downloads `yolov11n.pt`, `yolov11s.pt`, `yolov11m.pt` if missing

### Data Pipeline
```
Webcam Feed → OpenCV Processing → YOLOv11 Detection
    ↓
Confidence Filtering → Waste Classification (settings.py lookup)
    ↓
Gemini AI Processing (if API key) → Logging (JSON + CSV)
    ↓
Streamlit UI Display + Analytics
```

---

## Critical Developer Workflows

### Running the Application
```bash
# Set Gemini API key (optional but recommended)
export GOOGLE_API_KEY="your-api-key-here"

# Start the Streamlit app
streamlit run app.py
```

### Training Custom Models
- Edit `train.py` with your dataset path (expects YOLO format with `data.yaml`)
- Run: `python train.py`
- Model trains 50 epochs on GPU (device=0), exports to ONNX
- Save trained model to `weights/best.pt` or `weights/yolov11[n|s|m].pt`

### Key Dependencies
- **ultralytics 8.14.0**: YOLO model loading/inference
- **streamlit 1.42.0**: Web UI
- **torch 2.6.0 + torchvision**: GPU acceleration (CUDA 11.8+ required for GPU mode)
- **google-generativeai 0.8.6**: Gemini API client
- **opencv-python-headless**: Video processing (headless for servers)

### Debugging & Environment
- Check GPU: `python -c "import torch; print(torch.cuda.is_available())"`
- Model inference uses half precision on GPU (`model.half()`)
- Falls back to CPU automatically if CUDA unavailable
- Streamlit session state holds `confidence` threshold and `model_name`

---

## Project-Specific Patterns

### Model Loading & Optimization
All model loading goes through `helper.load_model()`:
- Auto-selects GPU if available, CPU otherwise
- Applies half precision (`model.half()`) for ~2x speedup on CUDA
- Raises graceful errors if model file missing (triggers auto-download)

### Waste Classification Lookup
Never hardcode waste categories—always use `settings.py` constants:
```python
recyclable, non_recyclable, hazardous = helper.classify_waste_type(detected_items)
```
The `classify_waste_type()` function uses set intersection: detected items are looked up against the three category lists. Add new waste types to `settings.RECYCLABLE/NON_RECYCLABLE/HAZARDOUS` only.

### Logging Architecture
- **Session logs** (`detection_logs.json`): Full detection sessions with metadata (model, confidence threshold, FPS, all detected items)
- **Statistics** (`detection_stats.csv`): Per-item aggregates (detection count, avg confidence, category)
- Always call `initialize_log_files()` before logging to ensure files exist
- Logged after each detection session completes

### Gemini Integration Points
- API key: `os.environ.get("GOOGLE_API_KEY")`
- Configure: `genai.configure(api_key=api_key)`
- Only active if key provided (checks wrapped with `GEMINI_AVAILABLE` flag)
- Used for generating recycling recommendations from detected waste types

---

## Integration Points & External Dependencies

### YOLOv11 Model Selection
- **Nano** (`yolov11n.pt`): 5ms inference, 2.6M params—use for real-time speed
- **Small** (`yolov11s.pt`): 10ms inference, 9.6M params—balanced (default)
- **Medium** (`yolov11m.pt`): 15ms inference, 20.1M params—maximum accuracy
- Selection in `app.py` via sidebar radio button → passed to `helper.load_model()`

### Gemini 2.0 Flash API
- Generate recycling recommendations from detected items
- Requires valid API key from [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- Optional—system works without key but AI recommendations disabled

### Roboflow Dataset v9
- [Link](https://universe.roboflow.com/ai-project-i3wje/waste-detection-vqkjo/model/3): 2,500+ images, 40+ waste classes
- Training uses YOLO format (expects `data.yaml` in dataset root)
- CC BY 4.0 license

---

## Common Modifications & Extension Points

### Adding New Waste Categories
1. Add class name to `settings.py` in the appropriate list (RECYCLABLE/NON_RECYCLABLE/HAZARDOUS)
2. Format: lowercase_with_underscores (e.g., "aluminum_foil", "light_bulb")
3. If adding hazardous categories, consider updating Gemini prompts in `helper.py` to emphasize safety

### Adjusting Detection Sensitivity
- **Confidence threshold**: Controlled via sidebar slider in `app.py` (0.1–0.9)
- Lower = more detections (may include false positives)
- Higher = fewer but more confident detections
- Stored in `st.session_state.confidence` and passed to model

### Switching Model Variants
- Edit `model_map` dictionary in `app.py` to change default or add new variants
- Download happens automatically if file missing
- Model file persists in `weights/` for offline use

### Customizing Gemini Prompts
- All Gemini API calls are in `helper.py`
- Look for `genai.GenerativeModel("gemini-2.0-flash")` instantiation
- Modify system prompt or input messages to change recommendation style

---

## Performance & Optimization Notes

- **Real-time processing**: 30 FPS on GPU (T4/V100), ~10 FPS on CPU
- **Memory**: Nano model (~2.6M params), fits on edge devices
- **Inference latency**: 5ms (Nano) to 15ms (Medium) on GPU
- **Half precision** reduces model size by ~50% and speeds inference ~2x on CUDA GPUs
- **CSV/JSON logging** is synchronous—avoid blocking UI during inference

---

## Testing & Validation

No formal test suite—validation done via:
- Live demo at [intelligent-waste-segregation-system.streamlit.app](https://intelligent-waste-segregation-system.streamlit.app)
- Detection logs reviewed for false positives/negatives
- mAP50 benchmark: 92% (precision 90%, recall 88%)
- Manual testing against diverse waste types in detection_stats.csv

---

## Quick Troubleshooting

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Webcam not detected | Wrong device index | Update `settings.WEBCAM_PATH` (try 0, 1, 2…) |
| CUDA OOM | Model too large for GPU memory | Switch to Nano model or reduce video resolution in OpenCV |
| Gemini API errors | Missing/invalid API key | Generate new key at [Google AI Studio](https://makersuite.google.com/app/apikey) |
| Slow inference | CPU mode active | Verify `torch.cuda.is_available()` returns True |

