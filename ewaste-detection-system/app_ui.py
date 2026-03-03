
import streamlit as st
import cv2
import tempfile
import time
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
from intelligence_layer import EWasteIntelligence
from PIL import Image
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="E-Waste Intelligence System",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. CONFIG: API KEYS & MODEL ---
# Sidebar for Settings
st.sidebar.title("Configuration")
st.sidebar.markdown("---")

# OpenRouter API Key Input
openrouter_api_key = st.sidebar.text_input("Enter OpenRouter API Key", value="", type="password", help="Required for AI-powered suggestions via OpenRouter. Get key from openrouter.ai")

# Initialize Intelligence Layer (Use Advanced if Key present)
@st.cache_resource
def load_intelligence(api_key=None):
    if api_key:
        try:
            from advanced_intelligence import AdvancedIntelligence
            return AdvancedIntelligence(api_key=api_key)
        except ImportError:
            st.warning("Advanced Intelligence module not found, falling back to basic.")
            return EWasteIntelligence()
    return EWasteIntelligence()

intelligence = load_intelligence(openrouter_api_key)

# Initialize Model
@st.cache_resource
def load_model(model_path):
    try:
        return YOLO(model_path)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# Model Configuration
model_path = st.sidebar.text_input("Model Path", "ewaste_project/yolov8x_custom_ewaste/weights/best.pt")
confidence = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.6, 0.05)
iou = st.sidebar.slider("IoU Threshold", 0.1, 1.0, 0.7, 0.05)

if not Path(model_path).exists():
    st.sidebar.warning(f"⚠️ Model not found at `{model_path}`.")
    st.sidebar.info("Using default `yolov8x.pt` for demonstration (Classes will be incorrect until trained).")
    model_path = "yolov8x.pt"

model = load_model(model_path)

# --- 2. LOGGING FUNCTIONALITY ---
LOG_FILE = "detection_log.csv"

def log_detection(class_name, confidence, recycling_type, reuse_suggestion):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = pd.DataFrame([{
        "Timestamp": timestamp,
        "Object": class_name,
        "Confidence": f"{confidence:.2f}",
        "Recycling Method": recycling_type,
        "Reuse Suggestion": reuse_suggestion
    }])
    
    # Save to CSV
    if not Path(LOG_FILE).exists():
        entry.to_csv(LOG_FILE, index=False)
    else:
        entry.to_csv(LOG_FILE, mode='a', header=False, index=False)

def get_recent_logs(limit=10):
    if Path(LOG_FILE).exists():
        try:
            df = pd.read_csv(LOG_FILE)
            return df.tail(limit).iloc[::-1]  # Show newest first
        except:
             return pd.DataFrame()
    return pd.DataFrame(columns=["Timestamp", "Object", "Confidence", "Recycling Method", "Reuse Suggestion"])


# --- 3. MAIN UI ---
st.title("♻️ Intelligent E-Waste Detection & Advisory")
st.markdown("""
**Specialized E-Waste Analysis System**
Detects **45+ specific electronic components** providing real-time recycling instructions and hazard warnings.
""")

tab1, tab2, tab3 = st.tabs(["📷 Live Analysis", "📤 Upload Image", "📜 Detection History"])

# --- TAB 1: Live Webcam ---
with tab1:
    col1, col2 = st.columns([2, 1.2]) # Adjusted ratio for better advice visibility
    
    with col1:
        start_cam = st.toggle("Start Live Detection", key="cam_toggle")
        cam_placeholder = st.empty()
        
    with col2:
        st.subheader("🤖 AI Advisor")
        advice_placeholder = st.empty()
    
    if start_cam and model:
        cap = cv2.VideoCapture(0)
        # Verify camera opened
        if not cap.isOpened():
            st.error("Could not open webcam.")
        else:
            # Optimize Camera Loop
            # We skip 'time.sleep' to run as fast as possible, Streamlit handles frame limiting naturally
            last_log_time = 0 
            LOG_INTERVAL = 2.0  # Log only once every 2 seconds per item to avoid spamming CSV

            while start_cam:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read from webcam.")
                    break
                
                # Run Inference
                results = model(frame, conf=confidence, iou=iou, verbose=False)
                
                detected_items_for_log = []
                current_advice_text = ""

                # Annotation on frame
                annotated_frame = frame.copy()

                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = model.names[cls_id] if model.names else str(cls_id)

                        # Draw Box
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Get Intelligence
                        # If API key used, we might call Gemini here, but to keep FPS high,
                        # we use the fast static dictionary first, maybe queue AI calls?
                        # For now, let's stick to dictionary for real-time speed, use AI for logging/display.
                        analysis = intelligence.analyze(class_name, conf)
                        
                        is_hazardous = analysis.get('safety_alert', {}).get('is_hazardous', False)
                        color = (0, 0, 255) if is_hazardous else (0, 255, 0)
                        
                        # Add visuals
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                        label = f"{class_name} {conf:.2f}"
                        cv2.putText(annotated_frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                        # Collect for Advice Panel & Logging
                        detected_items_for_log.append((class_name, conf, analysis))
                
                # Update Video Feed
                frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                cam_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)

                # Update Advice Panel (Only show unique items to reduce clutter)
                unique_detections = {item[0]: item[2] for item in detected_items_for_log}
                
                with advice_placeholder.container():
                    if unique_detections:
                        for name, data in unique_detections.items():
                            with st.chat_message("assistant", avatar="🤖"):
                                st.markdown(f"**Detected: {name.upper()}**")
                                
                                # Priority: Show Hazard First
                                if data.get('safety_alert', {}).get('is_hazardous'):
                                    st.error(f"🚨 **HAZARD**: {data['safety_alert']['hazard_details']}")
                                
                                # Show Recycling Info
                                st.info(f"♻️ **Recycle**: {data['recycling_recommendation']}")
                                st.write(f"💡 **Reuse**: {data['reuse_suggestion']}")
                                st.caption(f"🌍 Carbon Benefit: {data['environmental_impact']['carbon_recovery_benefit']}")
                                
                                # Log to CSV periodically
                                if time.time() - last_log_time > LOG_INTERVAL:
                                    log_detection(name, data['confidence'], data['recycling_recommendation'], data['reuse_suggestion'])
                                    last_log_time = time.time()
                    else:
                        st.info("Waiting for E-Waste detection...")

            cap.release()


# --- TAB 2: Upload Image ---
with tab2:
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        
        # Run Inference
        results = model(img_array, conf=confidence, iou=iou)
        
        annotated_img = img_array.copy()
        video_log = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls_id] if model.names else str(cls_id)
                
                # Analyze (Use AI if key available - this is one-shot so slower calling is fine)
                # Currently calling standard analyze, add AI call if implemented in AdvancedIntelligence
                analysis = intelligence.analyze(class_name, conf)
                
                # Check for AI enhancement if available in object
                if hasattr(intelligence, 'analyze_with_ai') and openrouter_api_key:
                     # This calls the Gemini API
                     analysis = intelligence.analyze_with_ai(class_name, conf)

                video_log.append(analysis)
                
                # Draw
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                is_hazardous = analysis.get('safety_alert', {}).get('is_hazardous', False)
                color = (255, 0, 0) if is_hazardous else (0, 255, 0) # RGB for Streamlit/PIL
                
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 3)
                label = f"{class_name} {conf:.2f}"
                cv2.putText(annotated_img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                # Log this static detection
                log_detection(class_name, conf, analysis['recycling_recommendation'], analysis['reuse_suggestion'])

        with col1:
             st.image(annotated_img, caption="Analyzed Image", use_column_width=True)
             
        with col2:
            st.header("📋 Analysis Report")
            if video_log:
                for i, det in enumerate(video_log):
                    with st.expander(f"#{i+1} {det['class'].upper()}", expanded=True):
                        # Use AI Suggestion if present (from AdvancedIntelligence)
                        if 'ai_suggestion' in det:
                            st.markdown(f"✨ **AI Expert Advice:** {det['ai_suggestion']}")
                        
                        m_col, r_col = st.columns(2)
                        with m_col:
                            st.write(f"**Material:** {', '.join(det['material_composition'])}")
                        with r_col:
                            st.write(f"**Action:** {det['recycling_recommendation']}")
                            
                        if det.get('safety_alert', {}).get('is_hazardous'):
                             st.error(f"🚨 HAZARD: {det['safety_alert']['hazard_details']}")
                             
                        st.caption(f"Reuse: {det['reuse_suggestion']}")


# --- TAB 3: Detection History ---
with tab3:
    st.header("📜 Real-time Detection Log")
    st.caption("Auto-refreshes every few seconds during camera operation.")
    
    if st.button("🔄 Refresh Log"):
        st.rerun()
        
    history_df = get_recent_logs(20)
    if not history_df.empty:
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        # Download Button
        csv = history_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV Log",
            csv,
            "ewaste_detection_log.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("No detections recorded yet.")
