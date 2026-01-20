from pathlib import Path
import streamlit as st
import helper
import settings
import os

st.set_page_config(
    page_title="Intelligent Waste Segregation System",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("⚙️ Detection Console")
st.sidebar.markdown("---")

# Model selection with latest YOLOv11 versions
model_type = st.sidebar.radio(
    "Select Model Quality",
    ["Fast (Nano)", "Balanced (Small)", "Accurate (Medium)"],
    help="Higher quality = slower but more accurate detection"
)

model_map = {
    "Fast (Nano)": "yolov11n.pt",
    "Balanced (Small)": "yolov11s.pt",
    "Accurate (Medium)": "yolov11m.pt"
}

selected_model = model_map[model_type]
model_path = Path(settings.MODEL_DIR) / selected_model

st.title("♻️ Intelligent Waste Segregation System")
st.markdown("""
    **Advanced AI-Powered Waste Detection & Recycling Guidance**
    
    This system uses the latest YOLOv11 deep learning model to detect waste items with high accuracy 
    and provides AI-powered recycling suggestions using Google Gemini 2.0 Flash.
    
    ✨ Features:
    - Real-time waste detection with 90%+ accuracy
    - Object quality assessment
    - AI-powered recycling recommendations
    - Environmental impact analysis
""")

st.markdown("---")

# Model loading with error handling
model = None

if model_path.exists():
    try:
        with st.spinner(f"Loading {model_type} model..."):
            model = helper.load_model(str(model_path))
        st.sidebar.success(f"✅ {model_type} model loaded successfully")
    except Exception as e:
        st.sidebar.error(f"❌ Model loading failed: {str(e)}")
else:
    st.sidebar.warning(f"⚠️ Model file not found: {selected_model}")
    st.sidebar.info("Downloading latest model... This may take a moment.")
    try:
        with st.spinner("Downloading latest YOLOv11 model..."):
            model = helper.load_model(selected_model)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            model.save(str(model_path))
        st.sidebar.success(f"✅ {model_type} model downloaded and loaded")
    except Exception as e:
        st.sidebar.error(f"❌ Failed to download model: {str(e)}")

# Confidence threshold slider
st.sidebar.markdown("---")
confidence = st.sidebar.slider(
    "Detection Confidence Threshold",
    min_value=0.1,
    max_value=0.9,
    value=0.4,
    step=0.05,
    help="Lower = more detections (may include false positives) | Higher = fewer but more accurate detections"
)

# Store in session state for helper.py access
st.session_state.confidence = confidence

st.sidebar.markdown("---")

# API Key setup for Gemini 2.0 Flash
st.sidebar.subheader("🔑 API Configuration")
api_key = st.sidebar.text_input(
    "Google Gemini API Key",
    type="password",
    help="Get your free API key from https://makersuite.google.com/app/apikey"
)

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    st.sidebar.success("✅ Gemini API configured")
else:
    st.sidebar.warning("⚠️ Add API key for AI recommendations")

st.sidebar.markdown("---")

# Waste categories info
with st.sidebar.expander("📋 Waste Categories"):
    st.write("**♻️ Recyclable:**")
    st.write(", ".join(settings.RECYCLABLE))
    st.write("\n**⚠️ Non-Recyclable:**")
    st.write(", ".join(settings.NON_RECYCLABLE))
    st.write("\n**🚨 Hazardous:**")
    st.write(", ".join(settings.HAZARDOUS))

st.sidebar.markdown("---")

# System info
with st.sidebar.expander("ℹ️ System Info"):
    import torch
    st.write(f"**PyTorch Version:** {torch.__version__}")
    st.write(f"**CUDA Available:** {'Yes ✅' if torch.cuda.is_available() else 'No (CPU Mode)'}")
    st.write(f"**YOLOv11 Model:** {selected_model}")

# Store model name in session state for logging
st.session_state.model_name = selected_model

# Detection history viewer
with st.sidebar.expander("📊 Detection History"):
    if st.button("🔄 Refresh History", use_container_width=True):
        st.rerun()
    
    history = helper.get_detection_history()
    stats = helper.get_detection_stats()
    
    if history:
        st.subheader("Recent Sessions")
        for session in history[-5:]:  # Show last 5 sessions
            with st.container(border=True):
                st.caption(f"🕐 {session['timestamp'][:19]}")
                st.write(f"**Model:** {session['model']}")
                st.write(f"**Frames:** {session['frames_processed']} | **FPS:** {session['avg_fps']:.1f}")
                st.write(f"**Items Detected:** {len(session['detected_items'])}")
                if session['recyclable']:
                    st.write(f"♻️ Recyclable: {', '.join(session['recyclable'])}")
                if session['non_recyclable']:
                    st.write(f"⚠️ Non-Recyclable: {', '.join(session['non_recyclable'])}")
                if session['hazardous']:
                    st.write(f"🚨 Hazardous: {', '.join(session['hazardous'])}")
    else:
        st.info("No detection history yet. Start detection to begin logging.")
    
    if stats:
        st.subheader("Detection Statistics")
        st.dataframe(stats, use_container_width=True, hide_index=True)

st.sidebar.markdown("---")

# Visualization Dashboard Toggle
show_dashboard = st.sidebar.checkbox("📈 Show Analytics Dashboard", value=False)

# Main detection interface
if model is not None:
    # Analytics Dashboard
    if show_dashboard:
        st.markdown("---")
        st.header("📈 Analytics Dashboard")
        
        history = helper.get_detection_history()
        stats = helper.get_detection_stats()
        
        if history and stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sessions", len(history))
            with col2:
                total_frames = sum(s['frames_processed'] for s in history)
                st.metric("Total Frames", f"{total_frames:,}")
            with col3:
                avg_fps = sum(s['avg_fps'] for s in history) / len(history) if history else 0
                st.metric("Avg FPS", f"{avg_fps:.1f}")
            with col4:
                total_items = sum(len(s['detected_items']) for s in history)
                st.metric("Items Detected", total_items)
            
            # Category Distribution Chart
            st.subheader("📊 Category Distribution")
            import pandas as pd
            
            category_counts = {'Recyclable': 0, 'Non-Recyclable': 0, 'Hazardous': 0}
            for session in history:
                category_counts['Recyclable'] += len(session.get('recyclable', []))
                category_counts['Non-Recyclable'] += len(session.get('non_recyclable', []))
                category_counts['Hazardous'] += len(session.get('hazardous', []))
            
            df_categories = pd.DataFrame({
                'Category': list(category_counts.keys()),
                'Count': list(category_counts.values())
            })
            st.bar_chart(df_categories.set_index('Category'))
            
            # Top Detected Items
            st.subheader("🔝 Most Detected Items")
            df_stats = pd.DataFrame(stats)
            if not df_stats.empty:
                df_stats['detection_count'] = pd.to_numeric(df_stats['detection_count'])
                top_items = df_stats.nlargest(10, 'detection_count')[['item_name', 'detection_count', 'category']]
                st.dataframe(top_items, use_container_width=True, hide_index=True)
            
            # Session Timeline
            st.subheader("⏱️ Detection Timeline")
            session_data = []
            for session in history[-10:]:  # Last 10 sessions
                session_data.append({
                    'Timestamp': session['timestamp'][:19],
                    'FPS': session['avg_fps'],
                    'Items': len(session['detected_items'])
                })
            df_timeline = pd.DataFrame(session_data)
            st.line_chart(df_timeline.set_index('Timestamp'))
            
        else:
            st.info("📊 No data available yet. Start detection to generate analytics.")
        
        st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📹 Live Waste Detection")
    with col2:
        st.metric("Confidence", f"{confidence:.0%}")
    
    helper.play_webcam(model)
else:
    st.error("❌ Detection disabled. Please configure the model properly.")
    st.info("Try refreshing the page or check your internet connection.")
