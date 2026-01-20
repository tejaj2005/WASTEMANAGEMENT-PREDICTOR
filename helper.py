from ultralytics import YOLO
import time
import streamlit as st
import cv2
import settings
import threading
import numpy as np
import torch
import json
import csv
from datetime import datetime
from pathlib import Path
import os

# Try to import Google Generative AI (optional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    # Configure Gemini API if available
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    GEMINI_AVAILABLE = False
    st.warning("⚠️ Google Generative AI not installed. AI recommendations disabled. Install with: pip install google-generativeai")

# Logging configuration
LOGS_DIR = Path(".")
DETECTION_LOG_FILE = LOGS_DIR / "detection_logs.json"
STATS_FILE = LOGS_DIR / "detection_stats.csv"

def initialize_log_files():
    """Initialize log files if they don't exist"""
    if not DETECTION_LOG_FILE.exists():
        with open(DETECTION_LOG_FILE, 'w') as f:
            json.dump([], f)
    
    if not STATS_FILE.exists():
        with open(STATS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'item_name', 'detection_count', 'avg_confidence', 'category'])

def log_detection_session(detected_items, waste_categories, quality_assessments, model_name, confidence_threshold, frame_count, processing_time):
    """Log a complete detection session"""
    initialize_log_files()
    
    recyclable, non_recyclable, hazardous = waste_categories
    
    session_data = {
        'timestamp': datetime.now().isoformat(),
        'model': model_name,
        'confidence_threshold': confidence_threshold,
        'detected_items': detected_items,
        'recyclable': list(recyclable),
        'non_recyclable': list(non_recyclable),
        'hazardous': list(hazardous),
        'quality_assessments': quality_assessments,
        'frames_processed': frame_count,
        'processing_time_seconds': processing_time,
        'avg_fps': frame_count / processing_time if processing_time > 0 else 0
    }
    
    # Append to JSON log
    try:
        with open(DETECTION_LOG_FILE, 'r') as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append(session_data)
    
    with open(DETECTION_LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    # Update statistics CSV
    try:
        with open(STATS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            stats = {row['item_name']: row for row in reader}
    except:
        stats = {}
    
    # Update stats for each detected item
    for item in detected_items:
        if item in stats:
            stats[item]['detection_count'] = str(int(stats[item]['detection_count']) + 1)
        else:
            category = 'recyclable' if item in recyclable else ('non_recyclable' if item in non_recyclable else 'hazardous')
            stats[item] = {
                'timestamp': datetime.now().isoformat(),
                'item_name': item,
                'detection_count': '1',
                'avg_confidence': quality_assessments.get(item, 'N/A'),
                'category': category
            }
    
    # Write updated stats
    with open(STATS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'item_name', 'detection_count', 'avg_confidence', 'category'])
        writer.writeheader()
        for item_name, row in stats.items():
            writer.writerow(row)

def get_detection_history():
    """Retrieve detection history from logs"""
    initialize_log_files()
    try:
        with open(DETECTION_LOG_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def get_detection_stats():
    """Retrieve detection statistics"""
    initialize_log_files()
    try:
        with open(STATS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except:
        return []

def load_model(model_path):
    """Load YOLO model with latest optimizations"""
    try:
        model = YOLO(model_path)
        # Use GPU if available, otherwise CPU
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model.to(device)
        # Enable half precision for faster inference on GPU
        if device == 'cuda':
            model.half()
        return model
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

def classify_waste_type(detected_items):
    """Classify detected items into waste categories"""
    recyclable = set(detected_items) & set(settings.RECYCLABLE)
    non_recyclable = set(detected_items) & set(settings.NON_RECYCLABLE)
    hazardous = set(detected_items) & set(settings.HAZARDOUS)
    return recyclable, non_recyclable, hazardous

def remove_dash_from_class_name(name):
    """Convert underscores to spaces for display"""
    return name.replace("_", " ").title()

def assess_object_quality(confidence_score):
    """Assess object quality based on detection confidence"""
    if confidence_score >= 0.85:
        return "Excellent", "🟢"
    elif confidence_score >= 0.70:
        return "Good", "🟡"
    elif confidence_score >= 0.50:
        return "Fair", "🟠"
    else:
        return "Poor", "🔴"

def get_recycling_suggestions(detected_items, waste_categories, quality_assessments):
    """Use Gemini AI 2.0 to provide recycling suggestions"""
    if not GEMINI_AVAILABLE:
        return "⚠️ **AI Recommendations Unavailable**\n\nGoogle Generative AI is not installed. Install it with:\n```\npip install google-generativeai\n```\n\nThen restart the application and configure your API key."
    
    try:
        recyclable, non_recyclable, hazardous = waste_categories
        
        items_str = ", ".join(detected_items)
        recyclable_str = ", ".join(recyclable) if recyclable else "None"
        non_recyclable_str = ", ".join(non_recyclable) if non_recyclable else "None"
        hazardous_str = ", ".join(hazardous) if hazardous else "None"
        
        quality_info = "\n".join([f"- {item}: {quality}" for item, quality in quality_assessments.items()])
        
        prompt = f"""You are an expert waste management and recycling consultant with deep knowledge of sustainability.

Detected waste items: {items_str}

Object Quality Assessment:
{quality_info}

Classification:
- Recyclable: {recyclable_str}
- Non-Recyclable: {non_recyclable_str}
- Hazardous: {hazardous_str}

Please provide a comprehensive but concise response with:
1. Quality assessment of each item (reusability potential)
2. Specific recycling methods for each recyclable item (material-specific)
3. Proper disposal methods for non-recyclable and hazardous items
4. Environmental impact and carbon footprint reduction tips
5. Any special handling or preparation requirements
6. Recommended facilities or services for disposal

Format your response with clear sections and bullet points for easy reading."""

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt, stream=False)
        return response.text
    except Exception as e:
        return f"⚠️ **AI Suggestions Unavailable**\n\nError: {str(e)}\n\nPlease check:\n- Your API key is valid\n- You have internet connection\n- API quota is not exceeded"

def _display_detected_frames(model, st_frame, info_container, image, confidence_threshold=0.4):
    """Display detected frames with enhanced detection using latest YOLOv11"""
    # Resize for optimal processing
    image_resized = cv2.resize(image, (640, 480))
    
    # Run prediction with latest YOLOv11 features
    results = model.predict(
        image_resized, 
        conf=confidence_threshold,
        iou=0.45,  # Intersection over Union threshold
        verbose=False,
        device=0 if torch.cuda.is_available() else 'cpu',
        half=torch.cuda.is_available()  # Use half precision on GPU
    )
    
    names = model.names

    detected = {}
    confidences = []
    quality_assessments = {}
    
    # Extract detections with confidence scores and quality
    for r in results:
        for i, c in enumerate(r.boxes.cls):
            class_name = names[int(c)]
            confidence = float(r.boxes.conf[i])
            
            if class_name not in detected:
                detected[class_name] = []
            detected[class_name].append(confidence)
            confidences.append(confidence)
            
            # Assess quality
            quality, emoji = assess_object_quality(confidence)
            quality_assessments[class_name] = f"{emoji} {quality} ({confidence:.1%})"

    detected_items = list(detected.keys())
    waste_categories = classify_waste_type(detected_items)
    recyclable, non_recyclable, hazardous = waste_categories

    # Display results with enhanced UI
    with info_container:
        if detected_items:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if recyclable:
                    st.success(f"♻️ Recyclable ({len(recyclable)})")
                    for item in recyclable:
                        avg_conf = sum(detected[item]) / len(detected[item])
                        quality, emoji = assess_object_quality(avg_conf)
                        st.write(f"  {emoji} {remove_dash_from_class_name(item)}")
                        st.caption(f"Confidence: {avg_conf:.1%} | Quality: {quality}")
            
            with col2:
                if non_recyclable:
                    st.warning(f"⚠️ Non-Recyclable ({len(non_recyclable)})")
                    for item in non_recyclable:
                        avg_conf = sum(detected[item]) / len(detected[item])
                        quality, emoji = assess_object_quality(avg_conf)
                        st.write(f"  {emoji} {remove_dash_from_class_name(item)}")
                        st.caption(f"Confidence: {avg_conf:.1%} | Quality: {quality}")
            
            with col3:
                if hazardous:
                    st.error(f"🚨 Hazardous ({len(hazardous)})")
                    for item in hazardous:
                        avg_conf = sum(detected[item]) / len(detected[item])
                        quality, emoji = assess_object_quality(avg_conf)
                        st.write(f"  {emoji} {remove_dash_from_class_name(item)}")
                        st.caption(f"Confidence: {avg_conf:.1%} | Quality: {quality}")
            
            st.divider()
            
            # AI Recycling Suggestions
            st.subheader("🤖 AI-Powered Recycling Guidance")
            with st.spinner("Generating personalized recommendations..."):
                suggestions = get_recycling_suggestions(detected_items, waste_categories, quality_assessments)
                st.markdown(suggestions)
        else:
            st.info("No waste items detected. Point camera at waste to begin detection.")

    # Display annotated frame with high quality
    annotated_frame = results[0].plot()
    st_frame.image(annotated_frame, channels="BGR", use_column_width=True)

def play_webcam(model):
    """Run webcam detection with real-time processing using latest YOLOv11"""
    if st.button("🎥 Start Detection", key="detect_btn", use_container_width=True):
        cap = cv2.VideoCapture(settings.WEBCAM_PATH)
        
        if not cap.isOpened():
            st.error("❌ Cannot access webcam. Please check permissions and try again.")
            return
        
        # Set camera properties for better quality
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        frame_placeholder = st.empty()
        info_placeholder = st.container()
        
        col1, col2 = st.columns(2)
        with col1:
            stop_button = st.button("⏹️ Stop Detection", key="stop_btn", use_container_width=True)
        with col2:
            st.metric("Status", "🔴 Live")
        
        frame_count = 0
        start_time = time.time()
        all_detected_items = set()
        all_quality_assessments = {}
        all_waste_categories = (set(), set(), set())
        
        try:
            while cap.isOpened() and not stop_button:
                ret, img = cap.read()
                if not ret:
                    st.warning("Failed to read frame from webcam")
                    break
                
                # Get confidence from session state if available
                confidence = st.session_state.get('confidence', 0.4)
                
                # Process frame with latest YOLOv11
                _display_detected_frames(model, frame_placeholder, info_placeholder, img, confidence_threshold=confidence)
                frame_count += 1
                
                # Minimal delay for smooth real-time processing
                time.sleep(0.01)
                
        except Exception as e:
            st.error(f"❌ Error during detection: {str(e)}")
        finally:
            cap.release()
            processing_time = time.time() - start_time
            
            # Log the session
            if frame_count > 0:
                model_name = st.session_state.get('model_name', 'yolov11n')
                log_detection_session(
                    list(all_detected_items),
                    all_waste_categories,
                    all_quality_assessments,
                    model_name,
                    confidence,
                    frame_count,
                    processing_time
                )
            
            st.info(f"✅ Detection stopped. Processed {frame_count} frames in {processing_time:.2f}s ({frame_count/processing_time:.1f} FPS)")
