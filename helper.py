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


def get_detection_stats() -> list[dict]:
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
    """Persist one complete camera session."""
    _ensure_log_files()
    recyclable, non_recyclable, hazardous = waste_categories

    session = {
        "timestamp":            datetime.now().isoformat(),
        "model":                model_name,
        "confidence_threshold": confidence_threshold,
        "detected_items":       detected_items,
        "recyclable":           list(recyclable),
        "non_recyclable":       list(non_recyclable),
        "hazardous":            list(hazardous),
        "quality_assessments":  quality_info,
        "frames_processed":     frame_count,
        "processing_time_seconds": elapsed,
        "avg_fps":              frame_count / elapsed if elapsed > 0 else 0,
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
                "recyclable" if item in recyclable
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
            f,
            fieldnames=["timestamp", "item_name", "detection_count",
                        "avg_confidence", "category"],
        )
        w.writeheader()
        for row in stats.values():
            w.writerow(row)


# ─── Model Helpers ───────────────────────────────────────

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


def classify_waste(items: list) -> tuple[set, set, set]:
    """Classify detected item names into (recyclable, non_recyclable, hazardous)."""
    s = set(items)
    return (
        s & set(settings.RECYCLABLE),
        s & set(settings.NON_RECYCLABLE),
        s & set(settings.HAZARDOUS),
    )


def _display_name(name: str) -> str:
    """Convert underscore class name to title-case label."""
    return name.replace("_", " ").title()


def _quality_tier(conf: float) -> tuple[str, str]:
    """Return (label, emoji) for a confidence score."""
    if conf >= 0.85:
        return "Excellent", "🟢"
    if conf >= 0.70:
        return "Good", "🟡"
    if conf >= 0.50:
        return "Fair", "🟠"
    return "Poor", "🔴"


# ─── Gemini AI ───────────────────────────────────────────

def get_recycling_suggestions(
    detected_items, waste_categories, quality_assessments
):
    """Call Gemini 2.0 Flash for comprehensive recycling guidance."""
    api_key = st.session_state.get("gemini_api_key")
    if not api_key:
        return (
            "⚠️ **AI Recommendations Unavailable**\n\n"
            "Enter your Google Gemini API key in the sidebar to unlock "
            "AI-powered recycling insights."
        )
    if not GEMINI_AVAILABLE:
        return "⚠️ **google-generativeai** package is not installed."

    try:
        genai.configure(api_key=api_key)
        recyclable, non_recyclable, hazardous = waste_categories

        fmt = lambda s: ", ".join(_display_name(i) for i in s) or "None"
        quality_lines = "\n".join(
            f"- {_display_name(k)}: {v}"
            for k, v in quality_assessments.items()
        )

        prompt = f"""You are an expert waste-management and environmental
sustainability consultant specialising in E-waste recycling
and material recovery.

🔍 DETECTED ITEMS: {fmt(detected_items)}

📊 QUALITY ASSESSMENT:
{quality_lines}

♻️ CLASSIFICATION:
• Recyclable / E-Waste: {fmt(recyclable)}
• Non-Recyclable:       {fmt(non_recyclable)}
• Hazardous:            {fmt(hazardous)}

Provide a concise, actionable analysis covering:
1️⃣ Item-by-item condition & reusability
2️⃣ Recycling methods (certified centres, preparations)
3️⃣ Environmental impact (toxins prevented, CO₂ saved)
4️⃣ Immediate action plan & safety precautions

Format with clear headers and emojis. Be concise but actionable."""

        model = genai.GenerativeModel("gemini-2.0-flash")
        resp = model.generate_content(prompt, stream=False)
        return resp.text
    except Exception as e:
        return (
            f"⚠️ **AI Processing Error**\n\nError: {e}\n\n"
            "**Troubleshooting:**\n"
            "1. Check if key is valid (starts with 'AIza')\n"
            "2. Check internet connection\n"
            "3. Verify Gemini API quota"
        )


# ─── Frame Detection ─────────────────────────────────────

def _process_frame(model, st_frame, info_box, image, conf_thresh=0.4):
    """Run detection on one frame and update the Streamlit UI."""
    img = cv2.resize(image, (640, 480))

    results = model.predict(
        img,
        conf=conf_thresh,
        iou=0.45,
        verbose=False,
        device=0 if torch.cuda.is_available() else "cpu",
        half=torch.cuda.is_available(),
    )

    names = model.names
    detected: dict[str, list[float]] = {}
    quality_map: dict[str, str] = {}

    for r in results:
        for i, c in enumerate(r.boxes.cls):
            cls = names[int(c)]
            conf = float(r.boxes.conf[i])
            detected.setdefault(cls, []).append(conf)
            label, emoji = _quality_tier(conf)
            quality_map[cls] = f"{emoji} {label} ({conf:.0%})"

    items = list(detected)
    recyclable, non_recyclable, hazardous = classify_waste(items)

    # ── Info panel ────────────────────────────────────────
    with info_box:
        if items:
            cols = st.columns(3)
            _show_category(cols[0], "♻️ Recyclable", recyclable, detected, "success")
            _show_category(cols[1], "⚠️ Non-Recyclable", non_recyclable, detected, "warning")
            _show_category(cols[2], "🚨 Hazardous", hazardous, detected, "error")

            st.divider()
            st.subheader("🤖 AI-Powered Recycling Guidance")
            with st.spinner("Generating recommendations…"):
                suggestions = get_recycling_suggestions(
                    items,
                    (recyclable, non_recyclable, hazardous),
                    quality_map,
                )
                st.markdown(suggestions)
        else:
            st.info("No waste items detected — point camera at waste to begin.")

    # ── Annotated frame ──────────────────────────────────
    st_frame.image(results[0].plot(), channels="BGR", use_container_width=True)


def _show_category(col, title, item_set, detected, style):
    """Render a single waste-category column."""
    if not item_set:
        return
    with col:
        getattr(st, style)(f"{title} ({len(item_set)})")
        for item in item_set:
            avg = sum(detected[item]) / len(detected[item])
            label, emoji = _quality_tier(avg)
            st.write(f"  {emoji} {_display_name(item)}")
            st.caption(f"Confidence: {avg:.0%} · Quality: {label}")


# ─── Webcam Loop ─────────────────────────────────────────

def play_webcam(model):
    """Main webcam detection loop."""
    st.subheader("📹 Live Waste Detection")

    run = st.toggle("🔴 Enable Camera", help="Toggle to start/stop detection")
    frame_area = st.empty()
    info_area  = st.container()

    if not run:
        st.info("👆 Toggle the switch above to start the camera.")
        return

    cap = cv2.VideoCapture(settings.WEBCAM_INDEX)
    if not cap.isOpened():
        st.error("❌ Cannot access webcam — check permissions and retry.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    frames = 0
    t0 = time.time()
    stop = st.button("⏹️ Stop & Save Log")

    try:
        while cap.isOpened() and not stop:
            ok, img = cap.read()
            if not ok:
                st.warning("Lost webcam feed.")
                break
            conf = st.session_state.get("confidence", 0.4)
            _process_frame(model, frame_area, info_area, img, conf)
            frames += 1
            time.sleep(0.001)
    except Exception as e:
        st.error(f"❌ Detection error: {e}")
    finally:
        cap.release()
        elapsed = time.time() - t0
        if frames:
            fps = frames / elapsed
            st.info(
                f"✅ Stopped — {frames} frames in {elapsed:.1f}s "
                f"({fps:.1f} FPS)"
            )
        if stop:
            st.rerun()
