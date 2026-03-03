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


# Model selection - Default to Best trained model
model_type = st.sidebar.radio(
    "Select Model",
    ["🏆 Custom Trained (Best)", "Fast (Nano)", "Balanced (Small)", "Accurate (Medium)"],
    index=0,
    help="🏆 Best = Custom trained on E-waste dataset | Others = Pre-trained YOLOv11 (General)"
)

model_map = {
    "🏆 Custom Trained (Best)": "weights/best.pt",
    "Fast (Nano)": "yolov11n.pt",
    "Balanced (Small)": "yolov11s.pt",
    "Accurate (Medium)": "yolov11m.pt"
}

# Get the selected model file name
selected_model = model_map[model_type]

# Determine the full model path
if selected_model.startswith("weights/"):
    # Local best.pt file
    model_path = Path(settings.MODEL_DIR) / selected_model.replace("weights/", "")
else:
    # Pre-trained models: Just use the filename, let YOLO handle download
    model_path = selected_model

st.title("♻️ Intelligent Waste Segregation System")
st.markdown("""
    **Advanced AI-Powered Waste Detection & Recycling Guidance**
    
    This system uses the latest YOLOv11 deep learning model to detect waste items with high accuracy 
    and provides AI-powered recycling suggestions using Google Gemini 2.0 Flash.
    
    ✨ Features:
    - Real-time E-waste & General waste detection
    - Object quality assessment
    - AI-powered recycling recommendations
    - Environmental impact analysis
""")

st.markdown("---")

# API Key Configuration
# API Key Configuration
st.sidebar.markdown("---")
with st.sidebar.expander("🔑 API Configuration", expanded=False):
    # Default API Key from settings
    default_api_key = getattr(settings, 'GEMINI_API_KEY', '')
    
    # Store in session state if not already set
    if 'gemini_api_key' not in st.session_state:
        st.session_state['gemini_api_key'] = default_api_key

    # Input field to override
    api_key_input = st.text_input(
        "Gemini API Key", 
        value=st.session_state['gemini_api_key'], 
        type="password", 
        help="Get key from aistudio.google.com"
    )

    if api_key_input:
        st.session_state['gemini_api_key'] = api_key_input
        st.success("✅ Configured")
    else:
        st.warning("⚠️ No API Key provided.")

# Model loading with error handling
model = None

@st.cache_resource
def load_yolo_model(model_path_str):
    """Load YOLO model and cache it"""
    try:
        return helper.load_model(model_path_str)
    except Exception as e:
        return None

with st.spinner(f"⏳ Loading {model_type}..."):
    model = load_yolo_model(str(model_path))

if model is not None:
    st.sidebar.success(f"✅ {model_type} loaded successfully")
else:
    st.sidebar.error("❌ Model loading failed")
    with st.error("⚠️ Model Failed to Load"):
        st.markdown(f"""
**Possible causes**:
- File not found or download failed: {model_path}
- Internet connection needed for first-time download
- Corrupted model file

**Solutions**:
1. **For 🏆 Custom Trained Model**: Verify `weights/best.pt` exists.
2. **For Pre-trained Models**: Check internet connection.
3. Refresh browser: F5
        """)

# Confidence threshold slider
st.sidebar.markdown("---")
confidence = st.sidebar.slider(
    "Detection Confidence Threshold",
    min_value=0.1,
    max_value=0.9,
    value=0.4,
    step=0.05,
    help="Lower = more detections | Higher = fewer but more accurate detections"
)

# Store in session state for helper.py access
st.session_state.confidence = confidence

st.sidebar.markdown("---")

# Waste categories info
with st.sidebar.expander("📋 Waste Categories"):
    st.write("**♻️ Recyclable:**")
    st.write("Paper, Plastic, Metal, Glass, E-waste Components")
    st.write("\n**⚠️ Non-Recyclable:**")
    st.write("Organic, Styrofoam, Contaminated items")
    st.write("\n**🚨 Hazardous:**")
    st.write("Batteries, Chemicals, Medical Waste")

st.sidebar.markdown("---")

# System info
with st.sidebar.expander("ℹ️ System Info"):
    import torch
    st.write(f"**PyTorch Version:** {torch.__version__}")
    st.write(f"**CUDA Available:** {'Yes ✅' if torch.cuda.is_available() else 'No (CPU Mode)'}")
    st.write(f"**YOLOv11 Model:** {selected_model}")
    if st.session_state.get('gemini_api_key'):
        st.write(f"**Gemini 2.0 Flash:** ✅ Configured")
    else:
        st.write(f"**Gemini 2.0 Flash:** ⚠️ Not Configured")

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
            with st.container():
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
    
    # Live Detection Section
    helper.play_webcam(model)
else:
    st.error("❌ Detection disabled. Please configure the model properly.")
    st.info("Try refreshing the page or check your internet connection.")
