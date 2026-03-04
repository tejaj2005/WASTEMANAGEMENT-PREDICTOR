"""
Intelligent Waste Segregation System — Production UI
"""
import streamlit as st
import helper, settings
import torch, json, pandas as pd
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Waste Segregation System",
    page_icon="♻️", layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root{--g:#00C896;--r:#FF4B6E;--y:#FFB84D;--b:#4FC3F7;--bg:rgba(255,255,255,.04);--bd:rgba(255,255,255,.08);--ra:12px}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important}
.main .block-container{padding:1.5rem 2rem;max-width:1400px}

section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0d1117 0%,#060a12 100%);
  border-right:1px solid var(--bd)}

div[data-testid="stMetric"]{
  background:var(--bg);border:1px solid var(--bd);
  border-radius:var(--ra);padding:.9rem 1.1rem;
  transition:transform .2s,box-shadow .2s}
div[data-testid="stMetric"]:hover{
  transform:translateY(-3px);
  box-shadow:0 6px 24px rgba(0,200,150,.18)}

details[data-testid="stExpander"]{
  border:1px solid var(--bd)!important;
  border-radius:var(--ra)!important;
  background:var(--bg)!important;transition:border-color .25s}
details[data-testid="stExpander"]:hover{border-color:var(--g)!important}

.stButton>button{
  width:100%;padding:.65rem 1rem;font-weight:600;
  border-radius:8px;transition:all .25s;border:1px solid var(--bd)}
.stButton>button:hover{
  transform:translateY(-1px);
  box-shadow:0 4px 14px rgba(0,200,150,.2);border-color:var(--g)}

.stSlider>div>div>div{background:linear-gradient(90deg,var(--g),#0090FF)!important}

.live-badge{
  display:inline-flex;align-items:center;gap:6px;
  padding:4px 12px;border-radius:20px;
  background:rgba(255,75,110,.15);border:1px solid var(--r);
  color:var(--r);font-size:.78rem;font-weight:700;
  animation:pulse 1.5s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

.pill{
  display:inline-flex;align-items:center;gap:4px;
  padding:4px 10px;border-radius:16px;
  font-size:.78rem;font-weight:600;margin:3px}
.pill-g{background:rgba(0,200,150,.12);border:1px solid var(--g);color:var(--g)}
.pill-y{background:rgba(255,184,77,.12);border:1px solid var(--y);color:var(--y)}
.pill-r{background:rgba(255,75,110,.12);border:1px solid var(--r);color:var(--r)}
.pill-b{background:rgba(79,195,247,.12);border:1px solid var(--b);color:var(--b)}

.card{
  background:var(--bg);border:1px solid var(--bd);
  border-radius:var(--ra);padding:1rem 1.2rem;margin-bottom:.5rem}

.section-header{
  font-size:1.1rem;font-weight:700;
  color:#FAFAFA;margin-bottom:.5rem}

hr{border-color:var(--bd)!important}
@keyframes fadeIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
h1,h2{animation:fadeIn .5s ease-out}
</style>""", unsafe_allow_html=True)

# ─── Plotly dark template ─────────────────────────────────
PLOT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#FAFAFA"),
    margin=dict(l=20, r=20, t=40, b=20),
)
PALETTE = ["#00C896","#4FC3F7","#FFB84D","#FF4B6E",
           "#7B68EE","#FF7043","#B2FF59","#F06292"]

# ─── Sidebar ──────────────────────────────────────────────
st.sidebar.title("⚙️ Detection Console")
st.sidebar.markdown("---")

_MODEL_MAP = {
    "🏆 Custom Trained (Best)": str(settings.BEST_MODEL),
    "⚡ Fast — Nano":            "yolo11n.pt",
    "⚖️ Balanced — Small":      "yolo11s.pt",
    "🎯 Accurate — Medium":     "yolo11m.pt",
}
model_type = st.sidebar.radio(
    "Detection Model", list(_MODEL_MAP.keys()), index=0,
    help="🏆 Best = custom-trained e-waste model · Others = YOLO11 general (auto-download)"
)
selected_model = _MODEL_MAP[model_type]

st.sidebar.markdown("---")
confidence = st.sidebar.slider(
    "Confidence Threshold", 0.10, 0.95, 0.35, 0.05,
    help="Lower = more detections · Higher = only certain detections"
)
st.session_state.confidence = confidence
st.session_state.model_name = selected_model

# API key
st.sidebar.markdown("---")
with st.sidebar.expander("🔑 Gemini API Key", expanded=False):
    if "gemini_api_key" not in st.session_state:
        st.session_state["gemini_api_key"] = settings.GEMINI_API_KEY
    k = st.text_input("API Key (starts with AIza…)",
                      value=st.session_state["gemini_api_key"],
                      type="password",
                      help="Free key → aistudio.google.com/app/apikey")
    if k:
        st.session_state["gemini_api_key"] = k
        st.success("✅ Saved")
    else:
        st.warning("⚠️ AI guidance disabled")

# System info
with st.sidebar.expander("ℹ️ System Info"):
    gpu = torch.cuda.is_available()
    st.write(f"**PyTorch** `{torch.__version__}`")
    st.write(f"**GPU** {'✅ ' + torch.cuda.get_device_name(0) if gpu else '❌ CPU only'}")
    st.write(f"**Model** `{Path(selected_model).name}`")
    st.write(f"**Gemini** {'✅' if st.session_state.get('gemini_api_key') else '⚠️ Missing'}")

# E-waste taxonomy expander
with st.sidebar.expander("🗃️ E-Waste Subcategories"):
    for key, meta in settings.EWASTE_TAXONOMY.items():
        n = len(meta["items"])
        st.markdown(f"**{meta['label']}** `{n} types`")
        st.caption(f"{meta['weee_cat']} · {meta['hazard_level']}")

# ─── Load Model ───────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _load(p: str):
    return helper.load_model(p)

with st.spinner(f"⏳ Loading {model_type}…"):
    model = _load(selected_model)

if model is not None:
    st.sidebar.success(f"✅ {model_type.split('—')[-1].strip()} ready")
else:
    st.sidebar.error("❌ Model failed to load")
    st.error(f"**Cannot load:** `{selected_model}`  —  ensure `weights/best.pt` exists or internet for auto-download.")
    st.stop()

# ─── Header ───────────────────────────────────────────────
h_col, badge_col = st.columns([5, 1])
with h_col:
    st.title("♻️ Intelligent Waste Segregation System")
with badge_col:
    is_live = bool(st.session_state.get("live_detections"))
    if is_live:
        st.markdown('<span class="live-badge">● LIVE</span>', unsafe_allow_html=True)

st.markdown(
    "> **Real-time AI detection** · YOLO11 + Gemini 2.0 Flash · 12 E-waste subcategories · "
    "WEEE Directive compliant · Product recommendations"
)
st.markdown("---")

# ════════════════════════════════════════════════════════════
#  ANALYTICS DASHBOARD
# ════════════════════════════════════════════════════════════
st.header("📊 Analytics Dashboard")

live      = st.session_state.get("live_detections")
history   = helper.get_detection_history()
stats     = helper.get_detection_stats()
has_live  = isinstance(live, dict) and len(live) > 0
has_hist  = len(history) > 0

# ── Dashboard tabs ────────────────────────────────────────
tab_live, tab_hist, tab_ewaste, tab_log = st.tabs(
    ["🔴 Live Session", "📈 History", "🔧 E-Waste Analysis", "📋 Detection Log"]
)

# ══════════════════════
#  TAB 1 — LIVE SESSION
# ══════════════════════
with tab_live:
    if has_live:
        lr   = st.session_state.get("live_recyclable",     [])
        lnr  = st.session_state.get("live_non_recyclable", [])
        lhaz = st.session_state.get("live_hazardous",      [])
        lq   = st.session_state.get("live_quality_map",    {})
        li   = st.session_state.get("live_item_infos",     {})

        # KPIs
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Unique Items",     len(live))
        c2.metric("♻️ Recyclable",    len(set(lr)))
        c3.metric("⚠️ Non-Recyclable",len(set(lnr)))
        c4.metric("🚨 Hazardous",     len(set(lhaz)))
        c5.metric("E-waste Types",
                  len({settings.ITEM_SUBCATEGORY.get(i) for i in live if i in settings.ITEM_SUBCATEGORY}))

        st.markdown("---")

        # Category pills
        col_r, col_n, col_h = st.columns(3)
        with col_r:
            st.markdown("### ♻️ Recyclable")
            for item in sorted(set(lr)):
                info = li.get(item, helper.get_item_info(item))
                cnt  = live.get(item, 0)
                dn   = info["display_name"]
                sc   = info["subcategory"]
                q    = lq.get(item, "")
                st.markdown(
                    f'<span class="pill pill-g">{dn} ×{cnt}</span>',
                    unsafe_allow_html=True
                )
                st.caption(f"📂 {sc}  ·  {q}")

        with col_n:
            st.markdown("### ⚠️ Non-Recyclable")
            for item in sorted(set(lnr)):
                cnt = live.get(item, 0)
                dn  = item.replace("_", " ").title()
                q   = lq.get(item, "")
                st.markdown(f'<span class="pill pill-y">{dn} ×{cnt}</span>', unsafe_allow_html=True)
                if q: st.caption(q)

        with col_h:
            st.markdown("### 🚨 Hazardous")
            for item in sorted(set(lhaz)):
                info = li.get(item, helper.get_item_info(item))
                cnt  = live.get(item, 0)
                dn   = info["display_name"]
                q    = lq.get(item, "")
                hz   = info["hazard_level"]
                st.markdown(f'<span class="pill pill-r">{dn} ×{cnt}</span>', unsafe_allow_html=True)
                st.caption(f"{hz}  ·  {q}")

        st.markdown("---")

        # ── Detection frequency bar + donut ──────────────
        if len(live) >= 1:
            col_bar, col_pie = st.columns([3, 2])
            with col_bar:
                st.subheader("🔢 Detection Frequency")
                df_live = pd.DataFrame(
                    [(helper.get_item_info(k)["display_name"], v,
                      helper.get_item_info(k)["subcategory"])
                     for k, v in sorted(live.items(), key=lambda x: -x[1])],
                    columns=["Item", "Count", "Subcategory"]
                )
                fig = px.bar(
                    df_live, x="Count", y="Item", orientation="h",
                    color="Subcategory", color_discrete_sequence=PALETTE,
                    title="Items Detected (this session)"
                )
                fig.update_layout(**PLOT, height=max(250, len(live)*40))
                st.plotly_chart(fig, use_container_width=True)

            with col_pie:
                st.subheader("📊 Category Split")
                cat_counts = {
                    "♻️ Recyclable":     len(set(lr)),
                    "⚠️ Non-Recyclable": len(set(lnr)),
                    "🚨 Hazardous":      len(set(lhaz)),
                }
                fig2 = go.Figure(go.Pie(
                    labels=list(cat_counts.keys()),
                    values=list(cat_counts.values()),
                    hole=.55,
                    marker_colors=["#00C896","#FFB84D","#FF4B6E"],
                ))
                fig2.update_layout(**PLOT, height=280,
                                   title="Category Distribution")
                st.plotly_chart(fig2, use_container_width=True)

        # ── Sunburst: subcategory → items ────────────────
        if li:
            st.subheader("🌐 E-Waste Taxonomy Tree")
            rows = []
            for item, cnt in live.items():
                info = li.get(item, helper.get_item_info(item))
                rows.append({
                    "Subcategory": info["subcategory"],
                    "Item":        info["display_name"],
                    "Count":       cnt,
                    "WEEE":        info["weee_code"],
                })
            df_sun = pd.DataFrame(rows)
            if not df_sun.empty:
                fig3 = px.sunburst(
                    df_sun, path=["Subcategory","Item"], values="Count",
                    color="Count", color_continuous_scale="teal",
                    title="Detected Items — Subcategory → Item"
                )
                fig3.update_layout(**PLOT, height=420)
                st.plotly_chart(fig3, use_container_width=True)

        # ── CO2 impact ───────────────────────────────────
        if live:
            st.subheader("🌍 Estimated Environmental Impact (This Session)")
            total_co2 = sum(settings.ITEM_CO2_PER_KG.get(i, 5)*0.3 for i in live)
            ci1, ci2, ci3 = st.columns(3)
            ci1.metric("♻️ CO₂ Prevented",     f"{total_co2:.1f} kg")
            ci2.metric("⚡ Energy Saved",       f"{total_co2*3.5:.0f} Wh")
            ci3.metric("🌳 Trees Equivalent",   f"{total_co2/21:.2f}")

    else:
        st.info(
            "🔴 **No live session active.**  \n"
            "Enable the camera below → point at waste items → "
            "the dashboard will update in real-time."
        )

# ══════════════════════
#  TAB 2 — HISTORY
# ══════════════════════
with tab_hist:
    if has_hist:
        # KPIs
        all_det  = [i for s in history for i in s.get("detected_items", [])]
        total_co2 = sum(s.get("estimated_co2_saved_kg", 0) for s in history)
        avg_fps   = sum(s["avg_fps"] for s in history) / len(history)

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Sessions",       len(history))
        c2.metric("Total Frames",   f"{sum(s['frames_processed'] for s in history):,}")
        c3.metric("Avg FPS",        f"{avg_fps:.1f}")
        c4.metric("Items Detected", len(set(all_det)))
        c5.metric("CO₂ Prevented",  f"{total_co2:.1f} kg")

        st.markdown("---")

        col_line, col_cat = st.columns([3, 2])

        with col_line:
            # Timeline: FPS & items per session
            df_time = pd.DataFrame([
                {"Session": f"#{i+1}  {s['timestamp'][:10]}",
                 "FPS": s["avg_fps"],
                 "Items": len(s.get("detected_items", [])),
                 "Frames": s["frames_processed"]}
                for i, s in enumerate(history[-15:])
            ])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_time["Session"], y=df_time["FPS"],
                name="FPS", line=dict(color="#00C896", width=2), mode="lines+markers"
            ))
            fig.add_trace(go.Bar(
                x=df_time["Session"], y=df_time["Items"],
                name="Items", marker_color="#4FC3F7", opacity=0.5, yaxis="y2"
            ))
            fig.update_layout(
                **PLOT, title="Session Timeline (last 15)",
                yaxis=dict(title="FPS"),
                yaxis2=dict(title="Items", overlaying="y", side="right"),
                height=320
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_cat:
            # Stacked category totals
            cats = {"Recyclable":0,"Non-Recyclable":0,"Hazardous":0}
            for s in history:
                cats["Recyclable"]     += len(s.get("recyclable",[]))
                cats["Non-Recyclable"] += len(s.get("non_recyclable",[]))
                cats["Hazardous"]      += len(s.get("hazardous",[]))
            fig2 = go.Figure(go.Bar(
                x=list(cats.keys()), y=list(cats.values()),
                marker_color=["#00C896","#FFB84D","#FF4B6E"]
            ))
            fig2.update_layout(**PLOT, title="Category Totals", height=320)
            st.plotly_chart(fig2, use_container_width=True)

        # ── Top items table ───────────────────────────────
        if stats:
            st.subheader("🔝 Most Detected Items (All Sessions)")
            df = pd.DataFrame(stats)
            df["detection_count"] = pd.to_numeric(df["detection_count"], errors="coerce").fillna(0)
            df = df.sort_values("detection_count", ascending=False).head(20)
            df_display = df[["item_name","detection_count","category",
                              "subcategory","weee_code","hazard_level"]].copy()
            df_display.columns = ["Item","Count","Category","Subcategory","WEEE","Hazard"]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Horizontal bar sorted
            fig3 = px.bar(
                df.head(12), x="detection_count", y="item_name",
                orientation="h", color="category",
                color_discrete_map={
                    "recyclable":"#00C896",
                    "non_recyclable":"#FFB84D",
                    "hazardous":"#FF4B6E"
                },
                title="Top 12 Detected Items"
            )
            fig3.update_layout(**PLOT, height=380)
            st.plotly_chart(fig3, use_container_width=True)

        # ── CO2 impact across sessions ────────────────────
        st.subheader("🌍 Cumulative Environmental Impact")
        ci1, ci2, ci3, ci4 = st.columns(4)
        ci1.metric("CO₂ Prevented",  f"{total_co2:.1f} kg")
        ci2.metric("Energy Saved",   f"{total_co2*3.5:.0f} Wh")
        ci3.metric("Trees Equiv.",   f"{total_co2/21:.2f}")
        ci4.metric("Landfill Diverted", f"{len(set(all_det))} item types")

    else:
        st.info("📈 No session history yet. Run a detection session to populate this tab.")

# ══════════════════════════
#  TAB 3 — E-WASTE ANALYSIS
# ══════════════════════════
with tab_ewaste:
    st.subheader("🔧 E-Waste Taxonomy & WEEE Categories")

    # Taxonomy overview table
    rows = []
    for key, meta in settings.EWASTE_TAXONOMY.items():
        rows.append({
            "Subcategory":   meta["label"],
            "WEEE Category": meta["weee_cat"],
            "WEEE Code":     meta["weee_code"],
            "Items":         len(meta["items"]),
            "Hazard":        meta["hazard_level"],
            "Recyclability": meta["recyclability"],
            "CO₂/kg saved":  f"{meta['co2_per_kg']:.0f} kg",
        })
    df_tax = pd.DataFrame(rows)
    st.dataframe(df_tax, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Treemap of taxonomy structure
    st.subheader("🌳 E-Waste Taxonomy Treemap")
    tree_rows = []
    for key, meta in settings.EWASTE_TAXONOMY.items():
        for item_key, item_name in meta["items"].items():
            tree_rows.append({
                "Category":  "E-Waste",
                "Sub":       meta["label"],
                "Item":      item_name,
                "CO2":       meta["co2_per_kg"],
            })
    df_tree = pd.DataFrame(tree_rows)
    fig_tree = px.treemap(
        df_tree, path=["Category","Sub","Item"],
        values="CO2", color="CO2",
        color_continuous_scale="teal",
        title="E-Waste Items by Subcategory (sized by CO₂ savings)"
    )
    fig_tree.update_layout(**PLOT, height=500)
    st.plotly_chart(fig_tree, use_container_width=True)

    # Items by subcategory bar
    st.subheader("📊 Items per Subcategory")
    sub_counts = {
        meta["label"]: len(meta["items"])
        for meta in settings.EWASTE_TAXONOMY.values()
    }
    fig_sub = px.bar(
        x=list(sub_counts.values()),
        y=list(sub_counts.keys()),
        orientation="h",
        color=list(sub_counts.values()),
        color_continuous_scale="teal",
        title="Number of Detectable Items per E-Waste Subcategory"
    )
    fig_sub.update_layout(**PLOT, height=380)
    st.plotly_chart(fig_sub, use_container_width=True)

    # WEEE category donut
    weee_groups: dict = {}
    for meta in settings.EWASTE_TAXONOMY.values():
        wcat = meta["weee_cat"].split("—")[-1].strip()
        weee_groups[wcat] = weee_groups.get(wcat, 0) + len(meta["items"])
    fig_weee = go.Figure(go.Pie(
        labels=list(weee_groups.keys()),
        values=list(weee_groups.values()),
        hole=.5, marker_colors=PALETTE,
    ))
    fig_weee.update_layout(**PLOT, title="WEEE Category Distribution", height=360)
    st.plotly_chart(fig_weee, use_container_width=True)

    # Full item catalogue
    with st.expander("📖 Full Item Catalogue"):
        cat_rows = []
        for key, meta in settings.EWASTE_TAXONOMY.items():
            for ik, iname in meta["items"].items():
                cat_rows.append({
                    "Item Key":      ik,
                    "Display Name":  iname,
                    "Subcategory":   meta["label"],
                    "WEEE Code":     meta["weee_code"],
                    "Hazard":        meta["hazard_level"],
                    "CO₂/kg":        meta["co2_per_kg"],
                })
        st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)

# ══════════════════════
#  TAB 4 — LOG TABLE
# ══════════════════════
with tab_log:
    st.subheader("📋 Detection Session Log")

    col_l, col_r = st.columns([3, 1])
    col_r.download_button(
        "⬇️ Export JSON", data=Path("detection_logs.json").read_text()
        if Path("detection_logs.json").exists() else "[]",
        file_name=f"waste_log_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json", use_container_width=True
    )
    if col_r.button("🗑️ Clear All Logs", use_container_width=True):
        Path("detection_logs.json").write_text("[]")
        Path("detection_stats.csv").unlink(missing_ok=True)
        st.success("Logs cleared."); st.rerun()

    if has_hist:
        for i, s in enumerate(reversed(history[-10:])):
            label = (
                f"#{len(history)-i}  ·  {s['timestamp'][:19]}  ·  "
                f"{Path(s['model']).name}  ·  "
                f"{s['frames_processed']} frames  ·  "
                f"{s['avg_fps']:.1f} FPS  ·  "
                f"{len(s.get('detected_items',[]))} items"
            )
            with st.expander(label):
                ms = s.get("items_metadata", {})

                cd1, cd2 = st.columns(2)
                with cd1:
                    st.metric("Frames",  s["frames_processed"])
                    st.metric("Avg FPS", f"{s['avg_fps']:.1f}")
                    st.metric("Duration", f"{s['processing_time_seconds']:.0f}s")
                with cd2:
                    st.metric("Recyclable",     len(s.get("recyclable",[])))
                    st.metric("Non-Recyclable", len(s.get("non_recyclable",[])))
                    st.metric("Hazardous",      len(s.get("hazardous",[])))

                if ms:
                    st.markdown("**Detected Items:**")
                    item_rows = []
                    for ik, m in ms.items():
                        item_rows.append({
                            "Item":        m.get("display_name", ik),
                            "Subcategory": m.get("subcategory", "—"),
                            "WEEE Code":   m.get("weee_code", "—"),
                            "Hazard":      m.get("hazard_level", "—"),
                            "Quality":     m.get("quality", "—"),
                        })
                    st.dataframe(pd.DataFrame(item_rows),
                                 use_container_width=True, hide_index=True)
    else:
        st.info("No sessions recorded yet.")

st.markdown("---")

# ════════════════════════════════════════════════════════════
#  LIVE DETECTION
# ════════════════════════════════════════════════════════════
helper.play_webcam(model)
