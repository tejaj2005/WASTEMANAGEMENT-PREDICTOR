# 📐 System Diagrams — Intelligent Waste Segregation System

> All diagrams reflect the actual codebase: `app.py`, `helper.py`, `settings.py`

### 🖼️ Visual Diagram References

| Diagram | Preview |
|---------|---------|
| Use Case | ![Use Case Diagram](docs/diagrams/use_case_diagram.png) |
| Class Diagram | ![Class Diagram](docs/diagrams/class_diagram.png) |
| Sequence Diagram | ![Sequence Diagram](docs/diagrams/sequence_diagram.png) |
| System Architecture | ![Architecture Diagram](docs/diagrams/architecture_diagram.png) |



## 1️⃣ Use Case Diagram

```mermaid
flowchart TB
    subgraph System["♻️ Intelligent Waste Segregation System"]
        UC1["🎯 Select Model Variant<br/><i>Nano / Small / Medium / Custom</i>"]
        UC2["🔧 Configure API Key<br/><i>Gemini 2.0 Flash</i>"]
        UC3["🎚️ Adjust Confidence<br/><i>Threshold 0.1 – 0.9</i>"]
        UC4["📹 Start Live Detection<br/><i>Webcam feed</i>"]
        UC5["⏹️ Stop Detection<br/><i>Save session log</i>"]
        UC6["👀 View Detection Results<br/><i>Categories + Quality</i>"]
        UC7["🤖 Get AI Recommendations<br/><i>Gemini recycling guidance</i>"]
        UC8["📊 View Analytics Dashboard<br/><i>Charts, history, stats</i>"]
        UC9["📜 View Detection History<br/><i>Past sessions</i>"]
    end

    User((👤 User))

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC8
    User --> UC9

    UC4 --> UC6
    UC6 --> UC7

    subgraph External["☁️ External Services"]
        GeminiAPI["Google Gemini<br/>2.0 Flash API"]
        YOLOHub["Ultralytics<br/>Model Hub"]
    end

    UC7 -.->|"API Call"| GeminiAPI
    UC1 -.->|"Auto-download"| YOLOHub
```

---

## 2️⃣ UML Class Diagram

```mermaid
classDiagram
    direction TB

    class settings_py["⚙️ settings.py"] {
        +Path ROOT
        +Path MODEL_DIR
        +Path BEST_MODEL
        +str GEMINI_API_KEY
        +int WEBCAM_INDEX
        +list~str~ RECYCLABLE
        +list~str~ NON_RECYCLABLE
        +list~str~ HAZARDOUS
    }

    class helper_py["🔧 helper.py"] {
        +Path LOG_FILE
        +Path STATS_FILE
        +bool GEMINI_AVAILABLE
        +Module genai
        --
        -_ensure_log_files() void
        +get_detection_history() list
        +get_detection_stats() list~dict~
        +log_detection_session(detected_items, waste_categories, quality_info, model_name, confidence_threshold, frame_count, elapsed) void
        +load_model(model_path: str) YOLO | None
        +classify_waste(items: list) tuple~set, set, set~
        -_display_name(name: str) str
        -_quality_tier(conf: float) tuple~str, str~
        +get_recycling_suggestions(detected_items, waste_categories, quality_assessments) str
        -_process_frame(model, st_frame, info_box, image, conf_thresh) void
        -_show_category(col, title, item_set, detected, style) void
        +play_webcam(model) void
    }

    class app_py["🖥️ app.py"] {
        +dict _MODEL_MAP
        +str model_type
        +str selected_model
        +Path model_path
        +float confidence
        +bool show_dash
        --
        -_load(path: str) YOLO | None
        +render_sidebar() void
        +render_hero() void
        +render_dashboard() void
        +main() void
    }

    class YOLO["📦 ultralytics.YOLO"] {
        +dict names
        +predict(image, conf, iou, verbose, device, half) Results
        +to(device) YOLO
        +half() YOLO
        +plot() ndarray
    }

    class GeminiModel["☁️ genai.GenerativeModel"] {
        +generate_content(prompt, stream) Response
    }

    class StreamlitUI["🌐 Streamlit"] {
        +set_page_config()
        +sidebar
        +columns()
        +spinner()
        +toggle()
        +slider()
        +metric()
        +image()
        +markdown()
        +bar_chart()
        +line_chart()
        +dataframe()
        +session_state
    }

    class LogFiles["💾 File Storage"] {
        +detection_logs.json
        +detection_stats.csv
    }

    class Webcam["📷 cv2.VideoCapture"] {
        +read() tuple~bool, ndarray~
        +isOpened() bool
        +set(prop, value) void
        +release() void
    }

    app_py --> settings_py : imports config
    app_py --> helper_py : calls detection functions
    app_py --> StreamlitUI : renders UI
    helper_py --> settings_py : reads categories
    helper_py --> YOLO : loads & runs model
    helper_py --> GeminiModel : AI suggestions
    helper_py --> LogFiles : read/write logs
    helper_py --> Webcam : captures frames
    helper_py --> StreamlitUI : displays results
```

---

## 3️⃣ Sequence Diagram

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant App as 🖥️ app.py
    participant H as 🔧 helper.py
    participant S as ⚙️ settings.py
    participant YOLO as 📦 YOLO11 Model
    participant Cam as 📷 Webcam
    participant Gem as ☁️ Gemini API
    participant Log as 💾 JSON/CSV Files

    Note over App: Streamlit starts

    App->>S: import settings<br/>(ROOT, MODEL_DIR, GEMINI_API_KEY,<br/>WEBCAM_INDEX, categories)
    App->>App: render sidebar<br/>(model_type, confidence, API key)

    U->>App: Select model variant
    App->>H: load_model(model_path)
    H->>YOLO: YOLO(model_path)
    alt GPU available
        H->>YOLO: model.to("cuda")
        H->>YOLO: model.half()
    end
    YOLO-->>H: model instance
    H-->>App: model

    U->>App: Enter Gemini API key
    App->>App: session_state["gemini_api_key"] = key

    U->>App: Toggle "Enable Camera" ON
    App->>H: play_webcam(model)

    H->>Cam: cv2.VideoCapture(WEBCAM_INDEX)
    H->>Cam: set resolution 1280×720

    loop Every Frame
        H->>Cam: cap.read()
        Cam-->>H: (True, frame)

        H->>H: _process_frame(model, frame, conf)
        H->>YOLO: model.predict(image, conf, iou)
        YOLO-->>H: results (boxes, classes, confidence)

        H->>H: classify_waste(items)
        Note over H: Match items against<br/>settings.RECYCLABLE<br/>settings.NON_RECYCLABLE<br/>settings.HAZARDOUS

        H->>H: _quality_tier(confidence)
        Note over H: 🟢≥85% 🟡≥70%<br/>🟠≥50% 🔴<50%

        H->>H: _show_category(recyclable)
        H->>H: _show_category(non_recyclable)
        H->>H: _show_category(hazardous)

        H->>Gem: get_recycling_suggestions(items, categories, quality)
        Gem-->>H: AI analysis text

        H->>App: st_frame.image(annotated_frame)
        H->>App: st.markdown(suggestions)
    end

    U->>App: Click "Stop & Save Log"
    H->>Cam: cap.release()
    H->>Log: log_detection_session()<br/>→ detection_logs.json<br/>→ detection_stats.csv
    H-->>App: "✅ Stopped — N frames, X FPS"

    U->>App: Enable Analytics Dashboard
    App->>H: get_detection_history()
    H->>Log: read detection_logs.json
    Log-->>H: session list
    App->>H: get_detection_stats()
    H->>Log: read detection_stats.csv
    Log-->>H: stats list
    App->>App: render charts<br/>(bar_chart, line_chart, metrics)
```

---

## 4️⃣ System Architecture Diagram

```mermaid
flowchart TB
    subgraph UserLayer["👤 USER LAYER"]
        Browser["🌐 Web Browser<br/><i>http://localhost:8501</i>"]
    end

    subgraph PresentationLayer["🖥️ PRESENTATION LAYER — app.py"]
        direction TB
        PageConfig["Page Config<br/><i>set_page_config()</i><br/><i>Custom CSS / Inter font</i>"]
        Sidebar["Sidebar Controls<br/><i>Model selector</i><br/><i>Confidence slider</i><br/><i>API key input</i><br/><i>Waste categories</i><br/><i>System info</i>"]
        Hero["Hero Section<br/><i>Title + feature table</i>"]
        LiveView["Live Detection View<br/><i>Annotated video frame</i><br/><i>Category breakdown</i><br/><i>AI recommendations</i>"]
        Dashboard["Analytics Dashboard<br/><i>Metrics cards</i><br/><i>Bar chart</i><br/><i>Line chart</i><br/><i>Top items table</i>"]
        History["Detection History<br/><i>Recent sessions</i><br/><i>Item statistics</i>"]
    end

    subgraph BusinessLayer["🔧 BUSINESS LAYER — helper.py"]
        direction TB
        ModelLoader["load_model()<br/><i>YOLO loading + GPU opt</i>"]
        FrameProcessor["_process_frame()<br/><i>Resize → Predict → Classify</i>"]
        Classifier["classify_waste()<br/><i>Set intersection with categories</i>"]
        QualityScore["_quality_tier()<br/><i>Confidence → tier mapping</i>"]
        AIEngine["get_recycling_suggestions()<br/><i>Gemini prompt + response</i>"]
        WebcamLoop["play_webcam()<br/><i>Frame capture loop</i>"]
        Logger["log_detection_session()<br/><i>JSON + CSV persistence</i>"]
        HistoryReader["get_detection_history()<br/>get_detection_stats()"]
    end

    subgraph ConfigLayer["⚙️ CONFIG LAYER — settings.py"]
        Paths["Paths<br/><i>ROOT, MODEL_DIR, BEST_MODEL</i>"]
        APIKey["API Keys<br/><i>GEMINI_API_KEY from .env</i>"]
        Camera["Camera<br/><i>WEBCAM_INDEX = 0</i>"]
        Categories["Waste Categories<br/><i>RECYCLABLE: 43 items</i><br/><i>NON_RECYCLABLE: 17 items</i><br/><i>HAZARDOUS: 10 items</i>"]
    end

    subgraph ExternalLayer["☁️ EXTERNAL SERVICES"]
        GeminiAPI["Google Gemini 2.0 Flash<br/><i>gemini-2.0-flash model</i><br/><i>generativeai SDK</i>"]
        UltralyticsHub["Ultralytics Hub<br/><i>YOLO11 model download</i>"]
    end

    subgraph HardwareLayer["🔌 HARDWARE"]
        Webcam["📷 Webcam<br/><i>cv2.VideoCapture</i><br/><i>1280×720 @ 30fps</i>"]
        GPU["⚡ GPU (optional)<br/><i>CUDA 11.8+</i><br/><i>FP16 half precision</i>"]
    end

    subgraph StorageLayer["💾 FILE STORAGE"]
        JSONLog["detection_logs.json<br/><i>Session history</i>"]
        CSVStats["detection_stats.csv<br/><i>Item statistics</i>"]
        ModelWeights["weights/best.pt<br/><i>Custom YOLO model 6.2 MB</i>"]
        EnvFile[".env<br/><i>GEMINI_API_KEY</i><br/><i>gitignored</i>"]
    end

    Browser <--> PresentationLayer
    PresentationLayer --> BusinessLayer
    BusinessLayer --> ConfigLayer
    Sidebar --> ModelLoader
    LiveView --> FrameProcessor
    Dashboard --> HistoryReader
    History --> HistoryReader

    ModelLoader --> UltralyticsHub
    ModelLoader --> ModelWeights
    ModelLoader --> GPU
    FrameProcessor --> Classifier
    FrameProcessor --> QualityScore
    FrameProcessor --> AIEngine
    WebcamLoop --> FrameProcessor
    WebcamLoop --> Webcam
    AIEngine --> GeminiAPI
    Logger --> JSONLog
    Logger --> CSVStats
    HistoryReader --> JSONLog
    HistoryReader --> CSVStats
    APIKey --> EnvFile
    Classifier --> Categories

    style UserLayer fill:#1a1a2e,stroke:#00C896,color:#fff
    style PresentationLayer fill:#16213e,stroke:#00C896,color:#fff
    style BusinessLayer fill:#0f3460,stroke:#00C896,color:#fff
    style ConfigLayer fill:#1a1a2e,stroke:#FFB84D,color:#fff
    style ExternalLayer fill:#2d1b69,stroke:#7B68EE,color:#fff
    style HardwareLayer fill:#1b2838,stroke:#4FC3F7,color:#fff
    style StorageLayer fill:#1b3a1b,stroke:#66BB6A,color:#fff
```

---

## 📝 Notes

### Storage (No Database)
This project uses **flat-file storage**, not a database:
- **`detection_logs.json`** — complete session data (JSON array)
- **`detection_stats.csv`** — aggregated item counts (CSV table)

No MongoDB, PostgreSQL, or any other database is required.

### File Responsibilities

| File | Role | Key Functions |
|------|------|--------------|
| **`app.py`** | Frontend / UI | Page config, sidebar, model loading, dashboard rendering |
| **`helper.py`** | Backend / Engine | YOLO inference, Gemini AI, webcam loop, logging |
| **`settings.py`** | Configuration | Paths, API keys, camera index, waste category lists |
| **`.env`** | Secrets | `GEMINI_API_KEY` (gitignored) |
