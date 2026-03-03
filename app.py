"""
Intelligent Waste Segregation System — Streamlit Application
"""
from pathlib import Path
import streamlit as st
import helper
import settings

# ─── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Intelligent Waste Segregation System",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS for Premium UI ────────────────────────────
st.markdown("""
<style>
/* ── Import Google Font ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root variables ─────────────────────────────────── */
:root {
    --accent:       #00C896;
    --accent-soft:  #00C89620;
    --danger:       #FF4B6E;
    --warn:         #FFB84D;
    --bg-card:      rgba(255,255,255,0.04);
    --border:       rgba(255,255,255,0.08);
    --radius:       12px;
}

/* ── Global typography ──────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Main content area ──────────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1200px;
}

/* ── Sidebar ────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        rgba(17,24,39,0.97) 0%,
        rgba(10,15,28,0.99) 100%);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--accent) !important;
}

/* ── Cards (metric boxes, expanders) ────────────────── */
div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,200,150,0.12);
}
div[data-testid="stMetric"] label {
    font-weight: 600 !important;
    letter-spacing: 0.02em;
}

/* ── Expanders ──────────────────────────────────────── */
details[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-card) !important;
    transition: border-color 0.25s;
}
details[data-testid="stExpander"]:hover {
    border-color: var(--accent) !important;
}

/* ── Buttons ────────────────────────────────────────── */
.stButton > button {
    width: 100%;
    padding: 0.65rem 1rem;
    font-weight: 600;
    font-size: 0.95rem;
    border-radius: 8px;
    transition: all 0.25s ease;
    border: 1px solid var(--border);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0,200,150,0.18);
    border-color: var(--accent);
}

/* ── Toggle / checkbox accent ───────────────────────── */
.stToggle label span[data-testid="stToggleLabel"] {
    font-weight: 500;
}

/* ── Slider ─────────────────────────────────────────── */
.stSlider > div > div > div {
    background: linear-gradient(90deg, var(--accent), #0090FF) !important;
}

/* ── Divider ────────────────────────────────────────── */
hr {
    border-color: var(--border) !important;
}

/* ── Success / warning / error alerts ───────────────── */
div[data-testid="stAlert"] {
    border-radius: 8px;
}

/* ── Smooth image rendering ─────────────────────────── */
img {
    border-radius: 8px;
}

/* ── Hero heading animation ─────────────────────────── */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0); }
}
h1 {
    animation: fadeSlideIn 0.6s ease-out;
}
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────
st.sidebar.title("⚙️ Detection Console")
st.sidebar.markdown("---")

# Model selection
model_type = st.sidebar.radio(
    "Select Model",
    ["🏆 Custom Trained (Best)", "Fast (Nano)",
     "Balanced (Small)", "Accurate (Medium)"],
    index=0,
    help=(
        "🏆 Best = your custom-trained E-waste model  ·  "
        "Others = pre-trained YOLO11 (general objects)"
    ),
)

_MODEL_MAP = {
    "🏆 Custom Trained (Best)": "weights/best.pt",
    "Fast (Nano)":              "yolo11n.pt",
    "Balanced (Small)":         "yolo11s.pt",
    "Accurate (Medium)":        "yolo11m.pt",
}

selected_model = _MODEL_MAP[model_type]

if selected_model.startswith("weights/"):
    model_path = settings.MODEL_DIR / selected_model.replace("weights/", "")
else:
    model_path = selected_model  # YOLO auto-downloads


# ─── API Key ──────────────────────────────────────────────
st.sidebar.markdown("---")
with st.sidebar.expander("🔑 API Configuration", expanded=False):
    default_key = settings.GEMINI_API_KEY
    if "gemini_api_key" not in st.session_state:
        st.session_state["gemini_api_key"] = default_key

    key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state["gemini_api_key"],
        type="password",
        help="Get a free key → aistudio.google.com/app/apikey",
    )
    if key_input:
        st.session_state["gemini_api_key"] = key_input
        st.success("✅ Key saved")
    else:
        st.warning("⚠️ No API key — AI suggestions disabled")


# ─── Hero Section ────────────────────────────────────────
st.title("♻️ Intelligent Waste Segregation System")
st.markdown("""
> **Real-time AI waste detection** powered by **YOLO11** and
> **Google Gemini 2.0 Flash**.

| Feature | Details |
|---------|---------|
| 🎯 Detection | 40+ waste types at **30 FPS** (GPU) |
| 🤖 AI Guidance | Recycling, hazard warnings, reuse tips |
| 📊 Analytics | Live dashboard with session history |
""")

st.markdown("---")


# ─── Load Model ──────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _load(path: str):
    return helper.load_model(path)


with st.spinner(f"⏳ Loading **{model_type}**…"):
    model = _load(str(model_path))

if model is not None:
    st.sidebar.success(f"✅ {model_type} loaded")
else:
    st.sidebar.error("❌ Model failed to load")
    st.error(f"""
**Model could not be loaded:** `{model_path}`

| Possible cause | Fix |
|----------------|-----|
| File missing   | Ensure `weights/best.pt` exists |
| No internet    | Needed for first-time YOLO download |
| Corrupt file   | Delete the `.pt` and re-download |

Refresh the page (F5) after fixing.
""")
    st.stop()


# ─── Confidence slider ───────────────────────────────────
st.sidebar.markdown("---")
confidence = st.sidebar.slider(
    "Detection Confidence",
    min_value=0.10,
    max_value=0.90,
    value=0.40,
    step=0.05,
    help="Lower → more detections  ·  Higher → fewer, more precise",
)
st.session_state.confidence = confidence
st.session_state.model_name = selected_model


# ─── Sidebar Info Panels ─────────────────────────────────
st.sidebar.markdown("---")

with st.sidebar.expander("📋 Waste Categories"):
    st.markdown("""
**♻️ Recyclable** — Paper, Plastic, Metal, Glass, E-waste\n
**⚠️ Non-Recyclable** — Organic, Styrofoam, Contaminated\n
**🚨 Hazardous** — Batteries, Chemicals, Medical
""")

with st.sidebar.expander("ℹ️ System Info"):
    import torch
    st.write(f"**PyTorch** {torch.__version__}")
    gpu = "Yes ✅" if torch.cuda.is_available() else "CPU only"
    st.write(f"**CUDA** {gpu}")
    st.write(f"**Model** `{selected_model}`")
    key_ok = "✅" if st.session_state.get("gemini_api_key") else "⚠️ missing"
    st.write(f"**Gemini API** {key_ok}")


# ─── Detection History ───────────────────────────────────
with st.sidebar.expander("📊 Detection History"):
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

    history = helper.get_detection_history()
    stats   = helper.get_detection_stats()

    if history:
        st.caption("**Recent sessions**")
        for s in history[-5:]:
            with st.container():
                st.caption(f"🕐 {s['timestamp'][:19]}")
                st.write(f"Model: {s['model']}  ·  "
                         f"Frames: {s['frames_processed']}  ·  "
                         f"FPS: {s['avg_fps']:.1f}")
                for label, key in [("♻️", "recyclable"),
                                   ("⚠️", "non_recyclable"),
                                   ("🚨", "hazardous")]:
                    items = s.get(key, [])
                    if items:
                        st.write(f"{label} {', '.join(items)}")
    else:
        st.info("No sessions yet — start detection to begin logging.")

    if stats:
        st.caption("**Item statistics**")
        st.dataframe(stats, use_container_width=True, hide_index=True)


# ─── Analytics Dashboard ─────────────────────────────────
st.sidebar.markdown("---")
show_dash = st.sidebar.checkbox("📈 Show Analytics Dashboard", value=False)

if show_dash:
    st.markdown("---")
    st.header("📈 Analytics Dashboard")

    history = helper.get_detection_history()
    stats   = helper.get_detection_stats()

    if history and stats:
        import pandas as pd

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sessions",    len(history))
        c2.metric("Total Frames", f"{sum(s['frames_processed'] for s in history):,}")
        avg_fps = sum(s["avg_fps"] for s in history) / len(history)
        c3.metric("Avg FPS",     f"{avg_fps:.1f}")
        c4.metric("Items Found", sum(len(s["detected_items"]) for s in history))

        # Category bar chart
        st.subheader("📊 Category Distribution")
        cats = {"Recyclable": 0, "Non-Recyclable": 0, "Hazardous": 0}
        for s in history:
            cats["Recyclable"]     += len(s.get("recyclable", []))
            cats["Non-Recyclable"] += len(s.get("non_recyclable", []))
            cats["Hazardous"]      += len(s.get("hazardous", []))
        st.bar_chart(
            pd.DataFrame({"Category": cats.keys(), "Count": cats.values()})
            .set_index("Category")
        )

        # Top items
        st.subheader("🔝 Most Detected Items")
        df = pd.DataFrame(stats)
        if not df.empty:
            df["detection_count"] = pd.to_numeric(df["detection_count"])
            st.dataframe(
                df.nlargest(10, "detection_count")
                  [["item_name", "detection_count", "category"]],
                use_container_width=True,
                hide_index=True,
            )

        # Timeline
        st.subheader("⏱️ Detection Timeline")
        rows = [
            {"Timestamp": s["timestamp"][:19],
             "FPS": s["avg_fps"],
             "Items": len(s["detected_items"])}
            for s in history[-10:]
        ]
        st.line_chart(pd.DataFrame(rows).set_index("Timestamp"))
    else:
        st.info("📊 No data yet — start detection to generate analytics.")

    st.markdown("---")


# ─── Live Detection ───────────────────────────────────────
helper.play_webcam(model)
