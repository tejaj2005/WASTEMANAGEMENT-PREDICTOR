"""
Intelligent Waste Segregation System — Detection Engine & AI Integration
"""
from ultralytics import YOLO
import time, json, csv
import streamlit as st
import cv2, numpy as np, torch
import settings
from datetime import datetime
from pathlib import Path
from collections import defaultdict

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# ─── Persistent File Storage ─────────────────────────────
LOG_FILE   = Path("detection_logs.json")
STATS_FILE = Path("detection_stats.csv")


def _ensure_log_files():
    if not LOG_FILE.exists():
        LOG_FILE.write_text("[]")
    if not STATS_FILE.exists():
        with open(STATS_FILE, "w", newline="") as f:
            csv.writer(f).writerow(
                ["timestamp", "item_key", "item_name", "detection_count",
                 "avg_confidence", "category", "subcategory",
                 "weee_code", "hazard_level"]
            )


def get_detection_history() -> list:
    _ensure_log_files()
    try:
        return json.loads(LOG_FILE.read_text())
    except Exception:
        return []


def get_detection_stats() -> list:
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
    """Write session to JSON log + update CSV item stats."""
    _ensure_log_files()
    recyclable, non_recyclable, hazardous = waste_categories

    # Build rich item metadata for the log
    items_meta = {}
    for item in detected_items:
        items_meta[item] = {
            "display_name":  settings.ITEM_DISPLAY_NAME.get(item, item.replace("_", " ").title()),
            "subcategory":   settings.SUBCATEGORY_LABELS.get(settings.ITEM_SUBCATEGORY.get(item, ""), "General"),
            "weee_code":     settings.ITEM_WEEE_CODE.get(item, "N/A"),
            "hazard_level":  settings.ITEM_HAZARD.get(item, "Unknown"),
            "quality":       quality_info.get(item, "N/A"),
        }

    session = {
        "timestamp":              datetime.now().isoformat(),
        "model":                  model_name,
        "confidence_threshold":   confidence_threshold,
        "detected_items":         list(detected_items),
        "items_metadata":         items_meta,
        "recyclable":             list(recyclable),
        "non_recyclable":         list(non_recyclable),
        "hazardous":              list(hazardous),
        "quality_assessments":    quality_info,
        "frames_processed":       frame_count,
        "processing_time_seconds":round(elapsed, 2),
        "avg_fps":                round(frame_count / elapsed, 1) if elapsed > 0 else 0,
        "estimated_co2_saved_kg": round(
            sum(settings.ITEM_CO2_PER_KG.get(i, 5.0) * 0.3
                for i in detected_items), 2
        ),
    }

    logs = get_detection_history()
    logs.append(session)
    LOG_FILE.write_text(json.dumps(logs, indent=2))

    # Update CSV
    try:
        with open(STATS_FILE) as f:
            stats = {r["item_key"]: r for r in csv.DictReader(f)}
    except Exception:
        stats = {}

    for item in detected_items:
        cat = (
            "recyclable"      if item in recyclable
            else "non_recyclable" if item in non_recyclable
            else "hazardous"
        )
        if item in stats:
            stats[item]["detection_count"] = str(int(stats[item]["detection_count"]) + 1)
        else:
            stats[item] = {
                "timestamp":       datetime.now().isoformat(),
                "item_key":        item,
                "item_name":       settings.ITEM_DISPLAY_NAME.get(item, item.replace("_", " ").title()),
                "detection_count": "1",
                "avg_confidence":  quality_info.get(item, "N/A"),
                "category":        cat,
                "subcategory":     settings.SUBCATEGORY_LABELS.get(
                                       settings.ITEM_SUBCATEGORY.get(item, ""), "General"),
                "weee_code":       settings.ITEM_WEEE_CODE.get(item, "N/A"),
                "hazard_level":    settings.ITEM_HAZARD.get(item, "Unknown"),
            }

    with open(STATS_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "timestamp", "item_key", "item_name", "detection_count",
            "avg_confidence", "category", "subcategory",
            "weee_code", "hazard_level"
        ])
        w.writeheader()
        for row in stats.values():
            w.writerow(row)


# ─── Model ────────────────────────────────────────────────

def load_model(model_path: str):
    """Load YOLO model with GPU optimization.
    Falls back to YOLOv8 equivalent if YOLO11 auto-download fails.
    """
    import ultralytics

    # Build fallback list: try exact name first, then yolov8 equivalent
    candidates = [model_path]
    name = Path(model_path).name  # e.g. "yolo11n.pt"
    if name.startswith("yolo11"):
        # yolo11n → yolov8n, yolo11s → yolov8s, etc.
        fb = "yolov8" + name.replace("yolo11", "")
        candidates.append(fb)

    last_err = None
    for candidate in candidates:
        try:
            p = Path(candidate)
            resolved = str(p.resolve()) if p.exists() else candidate
            model = YOLO(resolved)
            if model is None:
                continue
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if device == "cuda":
                model = model.to(device)
                model.half()
            return model
        except Exception as exc:
            last_err = exc
            continue

    # All candidates failed — print helpful info to stderr/log
    print(f"[helper.load_model] All candidates failed for '{model_path}': {last_err}")
    print(f"[helper.load_model] Ultralytics version: {ultralytics.__version__}")
    return None



# ─── Classification ───────────────────────────────────────

def classify_waste(items: list) -> tuple:
    """Return (recyclable, non_recyclable, hazardous) sets."""
    s = set(items)
    return (
        s & set(settings.RECYCLABLE),
        s & set(settings.NON_RECYCLABLE),
        s & set(settings.HAZARDOUS),
    )


def get_item_info(item: str) -> dict:
    """Return rich metadata for any detected item key."""
    subcat_key = settings.ITEM_SUBCATEGORY.get(item)
    # Map COCO class names transparently
    coco_mapped = settings.COCO_TO_EWASTE.get(item, item)
    if subcat_key is None:
        subcat_key = settings.ITEM_SUBCATEGORY.get(coco_mapped)

    return {
        "key":           item,
        "display_name":  settings.ITEM_DISPLAY_NAME.get(item)
                         or settings.ITEM_DISPLAY_NAME.get(coco_mapped)
                         or item.replace("_", " ").title(),
        "subcategory":   settings.SUBCATEGORY_LABELS.get(subcat_key, "♻️ General Recyclable"),
        "subcategory_key": subcat_key or "general",
        "weee_cat":      settings.ITEM_WEEE_CAT.get(item, "General Waste"),
        "weee_code":     settings.ITEM_WEEE_CODE.get(item, "N/A"),
        "hazard_level":  settings.ITEM_HAZARD.get(item, "🟢 Low"),
        "recyclability": settings.ITEM_RECYCLABILITY.get(item, "Standard recycling"),
        "co2_per_kg":    settings.ITEM_CO2_PER_KG.get(item, 5.0),
    }


def _quality_tier(conf: float) -> tuple:
    if conf >= 0.85: return "Excellent", "🟢"
    if conf >= 0.70: return "Good",      "🟡"
    if conf >= 0.50: return "Fair",      "🟠"
    return "Poor", "🔴"


# ─── AI / Gemini ──────────────────────────────────────────

def get_recycling_suggestions(detected_items, waste_categories, quality_assessments):
    """Call Gemini with rich taxonomy context."""
    api_key = st.session_state.get("gemini_api_key")
    if not api_key:
        return (
            "⚠️ **AI Guidance Unavailable** — Enter your Gemini API key in the sidebar.\n\n"
            "Get a free key → [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)"
        )
    if not GEMINI_AVAILABLE:
        return "⚠️ `google-generativeai` not installed. Run `pip install google-generativeai`"

    try:
        genai.configure(api_key=api_key)
        recyclable, non_recyclable, hazardous = waste_categories

        # Build taxonomy-enriched item descriptions
        item_details = []
        for item in detected_items:
            info = get_item_info(item)
            item_details.append(
                f"• **{info['display_name']}** "
                f"({info['subcategory']}, {info['weee_code']}, "
                f"Hazard: {info['hazard_level']}, "
                f"Quality: {quality_assessments.get(item, 'N/A')})"
            )

        prompt = f"""You are a certified e-waste management expert (WEEE Directive specialist).

🔍 DETECTED E-WASTE ITEMS:
{chr(10).join(item_details)}

♻️ CLASSIFICATION:
• Recyclable/E-waste : {', '.join(info['display_name'] for i in recyclable for info in [get_item_info(i)])}
• Non-Recyclable     : {', '.join(i.replace('_',' ').title() for i in non_recyclable)}
• Hazardous          : {', '.join(info['display_name'] for i in hazardous for info in [get_item_info(i)])}

Provide a concise expert response with these exact sections:

## 1️⃣ Item-by-Item Analysis
Brief description of each item's materials, condition assessment, and key concern.

## 2️⃣ WEEE Compliance & Disposal
Which WEEE drop-off / certified recycler handles each item. Specific preparation steps (data wipe, battery removal).

## 3️⃣ 🛒 Eco-Alternative Product Recommendations
For each detected item type, suggest 1-2 refurbished or more sustainable alternatives with:
- Product suggestion
- Why it reduces waste
- Estimated price range (INR)

## 4️⃣ Environmental Impact
Estimated: CO₂ prevented, toxic materials kept from landfill, precious metals recoverable.

## 5️⃣ Action Plan (Priority Order)
3-5 specific next steps with urgency level (🔴 Immediate / 🟡 This Week / 🟢 This Month).

Keep it concise, practical, and India-relevant."""

        model_obj = genai.GenerativeModel("gemini-2.0-flash")
        resp = model_obj.generate_content(prompt, stream=False)
        return resp.text
    except Exception as e:
        return f"⚠️ **AI Error:** {e}\n\nCheck key validity and internet connection."


# ─── Camera & Frame Processing ───────────────────────────

def _open_camera(index: int):
    """Try multiple backends and resolutions for best camera quality."""
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    resolutions = [(1920, 1080), (1280, 720), (864, 480), (640, 480)]

    cap = None
    for backend in backends:
        c = cv2.VideoCapture(index, backend)
        if c.isOpened():
            cap = c
            break

    if cap is None or not cap.isOpened():
        return None, (640, 480)

    # Try best resolution
    actual_w, actual_h = 640, 480
    for w, h in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        got_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        got_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if got_w >= w * 0.9:   # within 10%
            actual_w, actual_h = got_w, got_h
            break

    cap.set(cv2.CAP_PROP_FPS,          30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS,    1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
    cap.set(cv2.CAP_PROP_BRIGHTNESS,   130)
    cap.set(cv2.CAP_PROP_CONTRAST,     35)
    cap.set(cv2.CAP_PROP_SHARPNESS,    50)

    return cap, (actual_w, actual_h)


def _enhance_frame(frame: np.ndarray) -> np.ndarray:
    """CLAHE contrast enhancement + mild sharpening."""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    kernel = np.array([[0, -0.5, 0], [-0.5, 3, -0.5], [0, -0.5, 0]], np.float32)
    return cv2.filter2D(enhanced, -1, kernel)


def _process_frame(model, st_frame, image, conf_thresh=0.35):
    """
    Detect objects, update session_state, render frame.
    Returns (items, recyclable, non_recyclable, hazardous, quality_map, item_infos).
    """
    enhanced = _enhance_frame(image)
    img = cv2.resize(enhanced, (640, 640))

    results = model.predict(
        img,
        conf=conf_thresh,
        iou=0.40,
        verbose=False,
        device=0 if torch.cuda.is_available() else "cpu",
        half=torch.cuda.is_available(),
        imgsz=640,
        agnostic_nms=True,
    )

    names   = model.names
    detected: dict = {}
    quality_map: dict = {}

    for r in results:
        for i, c in enumerate(r.boxes.cls):
            raw  = names[int(c)]
            # Map COCO → e-waste if applicable
            item = settings.COCO_TO_EWASTE.get(raw, raw)
            conf = float(r.boxes.conf[i])
            detected.setdefault(item, []).append(conf)
            label, emoji = _quality_tier(conf)
            quality_map[item] = f"{emoji} {label} ({conf:.0%})"

    items = list(detected)
    recyclable, non_recyclable, hazardous = classify_waste(items)
    item_infos = {item: get_item_info(item) for item in items}

    # ── Update live session_state ─────────────────────────
    live = st.session_state.setdefault("live_detections", {})
    for item in items:
        live[item] = live.get(item, 0) + 1
    st.session_state["live_recyclable"]       = list(i for i in live if i in settings.RECYCLABLE)
    st.session_state["live_non_recyclable"]   = list(i for i in live if i in settings.NON_RECYCLABLE)
    st.session_state["live_hazardous"]        = list(i for i in live if i in settings.HAZARDOUS)
    st.session_state["live_quality_map"]      = quality_map
    st.session_state["live_item_infos"]       = item_infos

    # ── Annotated frame at crisp display size ────────────
    annotated = results[0].plot(line_width=2, font_size=10)
    display   = cv2.resize(annotated, (960, 540), interpolation=cv2.INTER_LANCZOS4)
    st_frame.image(display, channels="BGR", use_container_width=True)

    return items, recyclable, non_recyclable, hazardous, quality_map, item_infos


# ─── Webcam Detection Loop ───────────────────────────────

def play_webcam(model):
    """Main webcam loop: detects, shows frame, throttles AI, logs on stop."""
    st.subheader("📹 Live Waste Detection")

    run = st.toggle("🔴 Enable Camera", value=False,
                    help="Toggle to start / stop the camera feed")

    frame_area = st.empty()
    ai_panel   = st.expander("🤖 AI Recycling Guidance + Product Recommendations",
                              expanded=True)

    if not run:
        st.info("👆 Toggle the switch above to start live detection.")
        for k in ["live_detections", "live_recyclable", "live_non_recyclable",
                  "live_hazardous", "live_quality_map", "live_item_infos"]:
            st.session_state.pop(k, None)
        return

    # Init accumulators
    for k in ["live_detections", "live_recyclable", "live_non_recyclable",
              "live_hazardous", "live_quality_map", "live_item_infos"]:
        st.session_state[k] = {} if k == "live_detections" else []
    st.session_state["live_item_infos"] = {}

    cap, (cam_w, cam_h) = _open_camera(settings.WEBCAM_INDEX)
    if cap is None:
        st.error("❌ Cannot open webcam — check permissions or try a different index in settings.py")
        return

    st.caption(f"📷 Camera: {cam_w}×{cam_h} px")

    frames          = 0
    t0              = time.time()
    last_ai_call    = 0.0
    AI_INTERVAL_S   = 10.0

    all_items:  set = set()
    all_rec:    set = set()
    all_nonrec: set = set()
    all_haz:    set = set()
    final_quality:  dict = {}
    final_infos:    dict = {}

    ctrl_l, ctrl_r = st.columns([1, 3])
    stop        = ctrl_l.button("⏹️ Stop & Save", use_container_width=True)
    fps_display = ctrl_r.empty()

    try:
        while cap.isOpened() and not stop:
            # Flush stale frames from buffer
            cap.grab(); cap.grab()
            ok, img = cap.retrieve()
            if not ok or img is None:
                ok, img = cap.read()
            if not ok or img is None:
                st.warning("⚠️ Lost camera feed.")
                break

            conf = st.session_state.get("confidence", 0.35)
            items, rec, nonrec, haz, qmap, infos = _process_frame(
                model, frame_area, img, conf
            )

            all_items  |= set(items)
            all_rec    |= rec
            all_nonrec |= nonrec
            all_haz    |= haz
            final_quality.update(qmap)
            final_infos.update(infos)
            frames += 1

            elapsed = time.time() - t0
            fps = frames / elapsed if elapsed > 0 else 0
            fps_display.markdown(
                f"🎞️ **{frames}** frames · ⚡ **{fps:.1f} FPS** · "
                f"🕐 {elapsed:.0f}s · 🔍 **{len(all_items)}** unique items"
            )

            # Throttled AI
            now = time.time()
            if items and (now - last_ai_call) > AI_INTERVAL_S:
                last_ai_call = now
                with ai_panel:
                    with st.spinner("Generating AI guidance…"):
                        txt = get_recycling_suggestions(
                            list(all_items),
                            (all_rec, all_nonrec, all_haz),
                            final_quality,
                        )
                        st.markdown(txt)

    except Exception as e:
        st.error(f"❌ Detection error: {e}")
    finally:
        cap.release()
        elapsed = time.time() - t0
        if frames > 0 and all_items:
            log_detection_session(
                detected_items=list(all_items),
                waste_categories=(all_rec, all_nonrec, all_haz),
                quality_info=final_quality,
                model_name=st.session_state.get("model_name", "unknown"),
                confidence_threshold=st.session_state.get("confidence", 0.35),
                frame_count=frames,
                elapsed=elapsed,
            )
            st.success(
                f"✅ Session logged — **{frames}** frames · "
                f"**{elapsed:.1f}s** · **{frames/elapsed:.1f} FPS** · "
                f"**{len(all_items)}** items saved."
            )
        elif frames > 0:
            st.info(f"Session ended — {frames} frames, no items detected.")
        if stop:
            st.rerun()
