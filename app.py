"""
Intelligent Waste Segregation System — Streamlit Application
"""
import streamlit as st
import helper
import settings
import torch
import pandas as pd
from pathlib import Path
from datetime import datetime

# ─── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Intelligent Waste Segregation System",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root {
    --accent:    #00C896;
    --danger:    #FF4B6E;
    --warn:      #FFB84D;
    --info:      #4FC3F7;
    --bg-card:   rgba(255,255,255,0.04);
    --border:    rgba(255,255,255,0.08);
    --radius:    12px;
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.main .block-container { padding: 1.5rem 2rem; max-width: 1300px; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,rgba(17,24,39,0.98) 0%,rgba(8,12,22,1) 100%);
    border-right: 1px solid var(--border);
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    transition: transform .2s, box-shadow .2s;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,200,150,.15);
}

/* Expanders */
details[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-card) !important;
    transition: border-color .25s;
}
details[data-testid="stExpander"]:hover { border-color: var(--accent) !important; }

/* Buttons */
.stButton > button {
    width: 100%; padding: .65rem 1rem;
    font-weight: 600; border-radius: 8px;
    transition: all .25s; border: 1px solid var(--border);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0,200,150,.2);
    border-color: var(--accent);
}

/* Live badge */
.live-badge {
    display: inline-block;
    padding: 3px 10px; border-radius: 20px;
    background: rgba(255,75,110,.2); border: 1px solid #FF4B6E;
    color: #FF4B6E; font-size: .75rem; font-weight: 700;
    animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }

/* Category pills */
.pill {
    display:inline-block; padding:3px 10px;
    border-radius:16px; font-size:.78rem; font-weight:600;
    margin: 2px;
}
.pill-green  { background:rgba(0,200,150,.15); border:1px solid #00C896; color:#00C896; }
.pill-yellow { background:rgba(255,184,77,.15); border:1px solid #FFB84D; color:#FFB84D; }
.pill-red    { background:rgba(255,75,110,.15); border:1px solid #FF4B6E; color:#FF4B6E; }

/* Slider accent */
.stSlider > div > div > div {
    background: linear-gradient(90deg, var(--accent), #0090FF) !important;
}

hr { border-color: var(--border) !important; }

@keyframes fadeIn {
  from{opacity:0;transform:translateY(-6px)} to{opacity:1;transform:translateY(0)}
}
h1,h2 { animation: fadeIn .5s ease-out; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────
st.sidebar.title("⚙️ Detection Console")
st.sidebar.markdown("---")

# Model selection
_MODEL_MAP = {
    "🏆 Custom Trained (Best)": str(settings.BEST_MODEL),
    "⚡ Fast (Nano)":           "yolo11n.pt",
    "⚖️ Balanced (Small)":     "yolo11s.pt",
    "🎯 Accurate (Medium)":    "yolo11m.pt",
}
model_type = st.sidebar.radio(
    "Detection Model",
    list(_MODEL_MAP.keys()),
    index=0,
    help="🏆 Custom = your fine-tuned e-waste model  ·  Others = general YOLO11 (auto-download)"
)
selected_model = _MODEL_MAP[model_type]

# Confidence + NMS sliders
st.sidebar.markdown("---")
confidence = st.sidebar.slider(
    "Confidence Threshold",
    min_value=0.10, max_value=0.95, value=0.35, step=0.05,
    help="Lower → catch more items (may have false positives)  ·  Higher → only sure detections"
)
st.session_state.confidence  = confidence
st.session_state.model_name  = selected_model

# ── API Key ──────────────────────────────────────────────
st.sidebar.markdown("---")
with st.sidebar.expander("🔑 API Configuration", expanded=False):
    if "gemini_api_key" not in st.session_state:
        st.session_state["gemini_api_key"] = settings.GEMINI_API_KEY

    key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state["gemini_api_key"],
        type="password",
        help="Free key → aistudio.google.com/app/apikey  (starts with AIza…)",
    )
    if key_input:
        st.session_state["gemini_api_key"] = key_input
        st.success("✅ Key saved for this session")
    else:
        st.warning("⚠️ No key — AI Guidance disabled")

# ── System Info ──────────────────────────────────────────
with st.sidebar.expander("ℹ️ System Info"):
    gpu_available = torch.cuda.is_available()
    st.write(f"**PyTorch** `{torch.__version__}`")
    st.write(f"**CUDA** {'✅ ' + torch.cuda.get_device_name(0) if gpu_available else '❌ CPU only'}")
    st.write(f"**Model** `{selected_model}`")
    key_ok = "✅ Set" if st.session_state.get("gemini_api_key") else "⚠️ Missing"
    st.write(f"**Gemini API** {key_ok}")

# ── Waste Categories Info ────────────────────────────────
with st.sidebar.expander("📋 Waste Categories"):
    st.markdown(f"""
**♻️ Recyclable** `{len(settings.RECYCLABLE)} types`  
Paper, Plastic, Metal, Glass, E-waste devices

**⚠️ Non-Recyclable** `{len(settings.NON_RECYCLABLE)} types`  
Foam, Styrofoam, Contaminated plastics

**🚨 Hazardous** `{len(settings.HAZARDOUS)} types`  
Batteries, Chemicals, Medical, Broken glass
""")

# ─── Load Model ──────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _load(path: str):
    return helper.load_model(path)


with st.spinner(f"⏳ Loading **{model_type}**…"):
    model = _load(selected_model)

if model is not None:
    st.sidebar.success(f"✅ {model_type} ready")
else:
    st.sidebar.error("❌ Model failed to load")
    st.error(f"""
**Cannot load model:** `{selected_model}`

| Cause | Fix |
|-------|-----|
| File missing | Ensure `weights/best.pt` exists |
| No internet | Required for first YOLO download |
| Corrupt file | Delete `.pt` file and retry |
""")
    st.stop()


# ─── Hero Section ────────────────────────────────────────
col_title, col_status = st.columns([4, 1])
with col_title:
    st.title("♻️ Intelligent Waste Segregation System")

camera_active = st.session_state.get("live_detections") is not None
with col_status:
    if camera_active:
        st.markdown('<span class="live-badge">🔴 LIVE</span>', unsafe_allow_html=True)

st.markdown("""
> **Real-time AI waste detection** using **YOLO11** + **Google Gemini 2.0 Flash** • 40+ waste types • Recycling guidance • Product recommendations
""")
st.markdown("---")


# ─── Real-Time Analytics (Live + Historical) ─────────────
st.header("📊 Analytics Dashboard")

live = st.session_state.get("live_detections", None)
history = helper.get_detection_history()
stats   = helper.get_detection_stats()

# Determine data source: live session_state OR saved history
has_live    = live is not None and len(live) > 0
has_history = len(history) > 0

if has_live:
    # ── LIVE real-time view ──────────────────────────────
    live_rec    = st.session_state.get("live_recyclable", [])
    live_nonrec = st.session_state.get("live_non_recyclable", [])
    live_haz    = st.session_state.get("live_hazardous", [])
    live_q      = st.session_state.get("live_quality_map", {})

    st.markdown('<span class="live-badge">🔴 LIVE SESSION</span>', unsafe_allow_html=True)
    st.caption("Dashboard updates every frame while camera is running")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unique Items",    len(live))
    c2.metric("Recyclable ♻️",  len(set(live_rec)))
    c3.metric("Non-Recyclable ⚠️", len(set(live_nonrec)))
    c4.metric("Hazardous 🚨",   len(set(live_haz)))

    st.markdown("---")

    # Category columns
    col_r, col_n, col_h = st.columns(3)
    with col_r:
        st.subheader("♻️ Recyclable")
        if live_rec:
            for item in sorted(set(live_rec)):
                cnt   = live.get(item, 0)
                q     = live_q.get(item, "")
                dn    = item.replace("_", " ").title()
                st.markdown(f'<span class="pill pill-green">{dn} ×{cnt}</span>', unsafe_allow_html=True)
                if q:
                    st.caption(q)
        else:
            st.caption("None detected yet")

    with col_n:
        st.subheader("⚠️ Non-Recyclable")
        if live_nonrec:
            for item in sorted(set(live_nonrec)):
                cnt = live.get(item, 0)
                q   = live_q.get(item, "")
                dn  = item.replace("_", " ").title()
                st.markdown(f'<span class="pill pill-yellow">{dn} ×{cnt}</span>', unsafe_allow_html=True)
                if q:
                    st.caption(q)
        else:
            st.caption("None detected yet")

    with col_h:
        st.subheader("🚨 Hazardous")
        if live_haz:
            for item in sorted(set(live_haz)):
                cnt = live.get(item, 0)
                q   = live_q.get(item, "")
                dn  = item.replace("_", " ").title()
                st.markdown(f'<span class="pill pill-red">{dn} ×{cnt}</span>', unsafe_allow_html=True)
                if q:
                    st.caption(q)
        else:
            st.caption("None detected yet")

    # Live detection frequency bar chart
    if live:
        st.markdown("---")
        st.subheader("🔢 Detection Frequency (Current Session)")
        df_live = pd.DataFrame(
            [(k.replace("_", " ").title(), v) for k, v in sorted(live.items(), key=lambda x: -x[1])],
            columns=["Item", "Count"]
        ).set_index("Item")
        st.bar_chart(df_live)

elif has_history:
    # ── HISTORICAL view ──────────────────────────────────
    st.caption("Showing saved session history. Start the camera to see live data.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sessions",      len(history))
    c2.metric("Total Frames",  f"{sum(s['frames_processed'] for s in history):,}")
    avg_fps = sum(s["avg_fps"] for s in history) / len(history)
    c3.metric("Avg FPS",       f"{avg_fps:.1f}")
    c4.metric("Unique Items",  len(set(i for s in history for i in s.get("detected_items", []))))

    st.markdown("---")

    # Category distribution
    st.subheader("📊 Category Distribution (All Sessions)")
    cats = {"Recyclable": 0, "Non-Recyclable": 0, "Hazardous": 0}
    for s in history:
        cats["Recyclable"]     += len(s.get("recyclable", []))
        cats["Non-Recyclable"] += len(s.get("non_recyclable", []))
        cats["Hazardous"]      += len(s.get("hazardous", []))
    st.bar_chart(pd.DataFrame({"Count": cats}).transpose())

    # Top detected items
    st.subheader("🔝 Most Detected Items")
    if stats:
        df = pd.DataFrame(stats)
        df["detection_count"] = pd.to_numeric(df["detection_count"])
        df["item_name"] = df["item_name"].str.replace("_", " ").str.title()
        st.dataframe(
            df.sort_values("detection_count", ascending=False)
              .head(15)[["item_name", "detection_count", "category", "avg_confidence"]],
            use_container_width=True, hide_index=True,
        )

    # Recent sessions timeline
    st.subheader("⏱️ Session Timeline")
    rows = [
        {"Timestamp": s["timestamp"][:19],
         "FPS":   s["avg_fps"],
         "Items": len(s.get("detected_items", []))}
        for s in history[-15:]
    ]
    st.line_chart(pd.DataFrame(rows).set_index("Timestamp"))

    # Session log accordion
    st.subheader("📋 Recent Sessions")
    for s in reversed(history[-5:]):
        label = f"🕐 {s['timestamp'][:19]}  ·  {s['model']}  ·  {s['frames_processed']} frames  ·  {s['avg_fps']:.1f} FPS"
        with st.expander(label):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown("**♻️ Recyclable**")
                for it in s.get("recyclable", []) or ["—"]:
                    st.write(f"• {it.replace('_', ' ').title()}")
            with col_b:
                st.markdown("**⚠️ Non-Recyclable**")
                for it in s.get("non_recyclable", []) or ["—"]:
                    st.write(f"• {it.replace('_', ' ').title()}")
            with col_c:
                st.markdown("**🚨 Hazardous**")
                for it in s.get("hazardous", []) or ["—"]:
                    st.write(f"• {it.replace('_', ' ').title()}")
else:
    st.info(
        "📊 **No data yet.** Enable the camera below → detect some items → "
        "stop the session. The dashboard will populate with real-time and saved data."
    )

if has_history and st.button("🗑️ Clear All Logs", type="secondary"):
    import json
    Path("detection_logs.json").write_text("[]")
    Path("detection_stats.csv").unlink(missing_ok=True)
    st.rerun()

st.markdown("---")

# ─── Live Detection ───────────────────────────────────────
helper.play_webcam(model)
