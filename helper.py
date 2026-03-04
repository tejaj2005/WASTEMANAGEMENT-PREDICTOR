"""
Intelligent Waste Segregation System — Detection Engine & AI Integration
"""
from ultralytics import YOLO
import time
import streamlit as st
import cv2
import settings
import numpy as np
import torch
import json
import csv
from datetime import datetime
from pathlib import Path

# ─── Gemini AI Setup ─────────────────────────────────────
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# ─── Logging ─────────────────────────────────────────────
LOG_FILE   = Path("detection_logs.json")
STATS_FILE = Path("detection_stats.csv")


def _ensure_log_files():
    """Create log files if they don't exist."""
    if not LOG_FILE.exists():
        LOG_FILE.write_text("[]")
    if not STATS_FILE.exists():
        with open(STATS_FILE, "w", newline="") as f:
            csv.writer(f).writerow(
                ["timestamp", "item_name", "detection_count",
                 "avg_confidence", "category"]
            )


def get_detection_history() -> list:
    """Return all logged detection sessions."""
    _ensure_log_files()
    try:
        return json.loads(LOG_FILE.read_text())
    except Exception:
        return []


def get_detection_stats() -> list:
    """Return aggregated per-item statistics."""
    _ensure_log_files()
    try:
        with open(STATS_FILE) as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def log_detection_session(
    detected_items, waste_categories, quality_info,
    model_name, confidence_threshold, frame_count, elapsed
):
    """Persist one complete camera session to JSON + CSV."""
    _ensure_log_files()
    recyclable, non_recyclable, hazardous = waste_categories

    session = {
        "timestamp":            datetime.now().isoformat(),
        "model":                model_name,
        "confidence_threshold": confidence_threshold,
        "detected_items":       list(detected_items),
        "recyclable":           list(recyclable),
        "non_recyclable":       list(non_recyclable),
        "hazardous":            list(hazardous),
        "quality_assessments":  quality_info,
        "frames_processed":     frame_count,
        "processing_time_seconds": round(elapsed, 2),
        "avg_fps":              round(frame_count / elapsed, 1) if elapsed > 0 else 0,
    }

    # Append to JSON log
    logs = get_detection_history()
    logs.append(session)
    LOG_FILE.write_text(json.dumps(logs, indent=2))

    # Update per-item CSV stats
    try:
        with open(STATS_FILE) as f:
            stats = {r["item_name"]: r for r in csv.DictReader(f)}
    except Exception:
        stats = {}

    for item in detected_items:
        if item in stats:
            stats[item]["detection_count"] = str(
                int(stats[item]["detection_count"]) + 1
            )
        else:
            cat = (
                "recyclable"     if item in recyclable
                else "non_recyclable" if item in non_recyclable
                else "hazardous"
            )
            stats[item] = {
                "timestamp":       datetime.now().isoformat(),
                "item_name":       item,
                "detection_count": "1",
                "avg_confidence":  quality_info.get(item, "N/A"),
                "category":        cat,
            }

    with open(STATS_FILE, "w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["timestamp", "item_name", "detection_count",
                           "avg_confidence", "category"]
        )
        w.writeheader()
        for row in stats.values():
            w.writerow(row)


# ─── Model Helpers ────────────────────────────────────────

def load_model(model_path: str):
    """Load a YOLO model; returns None on failure."""
    try:
        p = Path(model_path)
        resolved = str(p.resolve()) if p.exists() else model_path
        model = YOLO(resolved)
        if model is None:
            return None
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            model = model.to(device)
            model.half()
        return model
    except Exception:
        return None


def classify_waste(items: list) -> tuple:
    """Returns (recyclable, non_recyclable, hazardous) as sets."""
    s = set(items)
    return (
        s & set(settings.RECYCLABLE),
        s & set(settings.NON_RECYCLABLE),
        s & set(settings.HAZARDOUS),
    )


def _display_name(name: str) -> str:
    return name.replace("_", " ").title()


def _quality_tier(conf: float) -> tuple:
    if conf >= 0.85: return "Excellent", "🟢"
    if conf >= 0.70: return "Good",      "🟡"
    if conf >= 0.50: return "Fair",      "🟠"
    return "Poor", "🔴"


# ─── Gemini AI ────────────────────────────────────────────

def get_recycling_suggestions(detected_items, waste_categories, quality_assessments):
    """Call Gemini 2.0 Flash for comprehensive recycling + product recommendations."""
    api_key = st.session_state.get("gemini_api_key")
    if not api_key:
        return (
            "⚠️ **AI Recommendations Unavailable**\n\n"
            "Enter your Google Gemini API key in the sidebar → "
            "[aistudio.google.com](https://aistudio.google.com/app/apikey)"
        )
    if not GEMINI_AVAILABLE:
        return "⚠️ `google-generativeai` package not installed. Run `pip install google-generativeai`"

    try:
        genai.configure(api_key=api_key)
        recyclable, non_recyclable, hazardous = waste_categories

        fmt  = lambda s: ", ".join(_display_name(i) for i in s) or "None"
        qlns = "\n".join(f"- {_display_name(k)}: {v}" for k, v in quality_assessments.items())

        prompt = f"""You are a world-class waste management & sustainability consultant.

🔍 DETECTED WASTE ITEMS: {fmt(detected_items)}

📊 QUALITY ASSESSMENT:
{qlns}

♻️ CLASSIFICATION:
• Recyclable / E-Waste : {fmt(recyclable)}
• Non-Recyclable       : {fmt(non_recyclable)}
• Hazardous            : {fmt(hazardous)}

Provide a structured, actionable response with these exact sections:

## 1️⃣ Item Analysis
For each detected item: material type, condition, reusability potential.

## 2️⃣ Recycling & Disposal Methods
Specific steps, preparation (cleaning, disassembly), and where to take each item.

## 3️⃣ 🛒 Product Recommendations
Suggest 2-3 eco-friendly alternative PRODUCTS or services the user should buy/use instead
of the detected waste item. Include: product name, why it's better, estimated price range.

## 4️⃣ Environmental Impact
CO₂ saved, toxins prevented, resource conservation stats.

## 5️⃣ Immediate Action Plan
Step-by-step next actions (Today / This Week / This Month).

Be concise, specific, and use emojis for scannability."""

        model_obj = genai.GenerativeModel("gemini-2.0-flash")
        resp = model_obj.generate_content(prompt, stream=False)
        return resp.text
    except Exception as e:
        return (
            f"⚠️ **AI Error:** {e}\n\n"
            "**Fix:** Check API key validity (starts with `AIza`), quota, and internet."
        )


# ─── Frame Processing ────────────────────────────────────

def _enhance_frame(frame: np.ndarray) -> np.ndarray:
    """Apply sharpening + brightness enhancement for better detection."""
    # Denoise slightly
    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    # Sharpen
    kernel = np.array([[ 0, -1,  0],
                       [-1,  5, -1],
                       [ 0, -1,  0]], dtype=np.float32)
    sharpened = cv2.filter2D(frame, -1, kernel)
    # CLAHE on L-channel for contrast
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _process_frame(model, st_frame, info_box, image, conf_thresh=0.4):
    """
    Run detection on one frame, update Streamlit UI.
    Returns (items, recyclable, non_recyclable, hazardous, quality_map).
    """
    # Enhance then resize to native YOLO size for best accuracy
    enhanced = _enhance_frame(image)
    img = cv2.resize(enhanced, (640, 640))

    results = model.predict(
        img,
        conf=conf_thresh,
        iou=0.45,
        verbose=False,
        device=0 if torch.cuda.is_available() else "cpu",
        half=torch.cuda.is_available(),
        imgsz=640,
        augment=False,       # keep fast; set True for test-time augment
        agnostic_nms=True,   # class-agnostic NMS → fewer duplicate boxes
    )

    names = model.names
    detected: dict = {}
    quality_map: dict = {}

    for r in results:
        for i, c in enumerate(r.boxes.cls):
            cls  = names[int(c)]
            conf = float(r.boxes.conf[i])
            detected.setdefault(cls, []).append(conf)
            label, emoji = _quality_tier(conf)
            quality_map[cls] = f"{emoji} {label} ({conf:.0%})"

    items = list(detected)
    recyclable, non_recyclable, hazardous = classify_waste(items)

    # ── Update live session_state counters ──────────────
    live = st.session_state.setdefault("live_detections", {})
    for item in items:
        live[item] = live.get(item, 0) + 1
    st.session_state["live_recyclable"]    = [i for i in live if i in settings.RECYCLABLE]
    st.session_state["live_non_recyclable"]= [i for i in live if i in settings.NON_RECYCLABLE]
    st.session_state["live_hazardous"]     = [i for i in live if i in settings.HAZARDOUS]
    st.session_state["live_quality_map"]   = quality_map

    # ── Info panel ──────────────────────────────────────
    with info_box:
        if items:
            cols = st.columns(3)
            _show_category(cols[0], "♻️ Recyclable",     recyclable,    detected, "success")
            _show_category(cols[1], "⚠️ Non-Recyclable", non_recyclable, detected, "warning")
            _show_category(cols[2], "🚨 Hazardous",       hazardous,     detected, "error")
        else:
            st.info("No waste detected — point camera at an item.")

    # ── Annotated frame (full-res BGR) ──────────────────
    annotated = results[0].plot(line_width=2, font_size=10)
    # Scale annotated back up to display size for clarity
    display   = cv2.resize(annotated, (960, 540), interpolation=cv2.INTER_LANCZOS4)
    st_frame.image(display, channels="BGR", use_container_width=True)

    return items, recyclable, non_recyclable, hazardous, quality_map


def _show_category(col, title, item_set, detected, style):
    """Render a single waste-category column."""
    if not item_set:
        return
    with col:
        getattr(st, style)(f"{title} ({len(item_set)})")
        for item in sorted(item_set):
            avg = sum(detected[item]) / len(detected[item])
            label, emoji = _quality_tier(avg)
            st.write(f"  {emoji} **{_display_name(item)}**")
            st.caption(f"Confidence: {avg:.0%} · Quality: {label}")


# ─── Webcam Loop ─────────────────────────────────────────

def play_webcam(model):
    """Main webcam detection loop with live logging and AI suggestion throttle."""
    st.subheader("📹 Live Waste Detection")

    run = st.toggle("🔴 Enable Camera", help="Toggle to start/stop detection")

    # Live detection panels
    frame_area  = st.empty()
    metrics_row = st.empty()
    info_area   = st.container()

    # AI panel — shown below detection
    ai_expander = st.expander("🤖 AI Recycling Guidance & Product Recommendations",
                               expanded=True)

    if not run:
        st.info("👆 Toggle the switch above to start the camera.")
        # Clear live session state when stopped
        for k in ["live_detections", "live_recyclable",
                  "live_non_recyclable", "live_hazardous", "live_quality_map"]:
            st.session_state.pop(k, None)
        return

    # ── Init session accumulators ──────────────────────
    st.session_state["live_detections"]     = {}
    st.session_state["live_recyclable"]     = []
    st.session_state["live_non_recyclable"] = []
    st.session_state["live_hazardous"]      = []
    st.session_state["live_quality_map"]    = {}

    cap = cv2.VideoCapture(settings.WEBCAM_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(settings.WEBCAM_INDEX)
    if not cap.isOpened():
        st.error("❌ Cannot access webcam — check permissions and retry.")
        return

    # Camera settings for best quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS,          30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)   # Minimize buffer lag
    cap.set(cv2.CAP_PROP_AUTOFOCUS,    1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)

    frames          = 0
    t0              = time.time()
    last_ai_time    = 0.0
    AI_INTERVAL     = 8.0        # seconds between Gemini calls
    all_items:  set = set()
    all_rec:    set = set()
    all_nonrec: set = set()
    all_haz:    set = set()
    final_quality:  dict = {}

    stop_col, fps_col = st.columns([1, 3])
    stop = stop_col.button("⏹️ Stop & Save Log", use_container_width=True)
    fps_display = fps_col.empty()

    try:
        while cap.isOpened() and not stop:
            # Drain camera buffer for the freshest frame
            for _ in range(2):
                cap.grab()
            ok, img = cap.retrieve()
            if not ok or img is None:
                ok, img = cap.read()
            if not ok or img is None:
                st.warning("Lost webcam feed.")
                break

            conf = st.session_state.get("confidence", 0.4)
            items, rec, nonrec, haz, qmap = _process_frame(
                model, frame_area, info_area, img, conf
            )

            # Accumulate across all frames
            all_items  |= set(items)
            all_rec    |= rec
            all_nonrec |= nonrec
            all_haz    |= haz
            final_quality.update(qmap)
            frames += 1

            # Live metrics
            elapsed = time.time() - t0
            fps = frames / elapsed if elapsed > 0 else 0
            fps_display.markdown(
                f"🎞️ **{frames}** frames · "
                f"⚡ **{fps:.1f} FPS** · "
                f"🕐 {elapsed:.0f}s · "
                f"🔍 **{len(all_items)}** unique items"
            )

            # Throttled AI call
            now = time.time()
            if items and (now - last_ai_time) > AI_INTERVAL:
                last_ai_time = now
                with ai_expander:
                    with st.spinner("🤖 Generating AI analysis + product recommendations…"):
                        suggestion = get_recycling_suggestions(
                            list(all_items),
                            (all_rec, all_nonrec, all_haz),
                            final_quality,
                        )
                        st.markdown(suggestion)

    except Exception as e:
        st.error(f"❌ Detection error: {e}")
    finally:
        cap.release()
        elapsed = time.time() - t0

        # ── SAVE SESSION LOG ─────────────────────────
        if frames > 0 and all_items:
            log_detection_session(
                detected_items=list(all_items),
                waste_categories=(all_rec, all_nonrec, all_haz),
                quality_info=final_quality,
                model_name=st.session_state.get("model_name", "unknown"),
                confidence_threshold=st.session_state.get("confidence", 0.4),
                frame_count=frames,
                elapsed=elapsed,
            )
            st.success(
                f"✅ Session saved — **{frames}** frames, "
                f"**{elapsed:.1f}s**, "
                f"**{elapsed and frames/elapsed:.1f} FPS**, "
                f"**{len(all_items)}** unique items logged."
            )
        elif frames > 0:
            st.info(f"Session ended — {frames} frames, no items detected.")

        if stop:
            st.rerun()
