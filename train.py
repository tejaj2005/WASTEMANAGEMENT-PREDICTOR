"""
AI E-Waste Object Detection System — YOLOv8x Training Script
Target: 95–99% accuracy · 100 classes · 50K–100K images
"""
import subprocess, sys, shutil, yaml, json, csv
from pathlib import Path
from datetime import datetime
import argparse

# ── Ensure dependencies ─────────────────────────────────────────
try:
    from ultralytics import YOLO
    import torch
except ImportError:
    print("[!] Installing dependencies…")
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "ultralytics", "torch", "torchvision"])
    from ultralytics import YOLO
    import torch

import settings

ROOT    = Path(__file__).parent
DATASET = ROOT / "dataset"
RUNS    = ROOT / "runs" / "ewaste"
WEIGHTS = ROOT / "weights"

WEIGHTS.mkdir(exist_ok=True)
RUNS.mkdir(parents=True, exist_ok=True)


# ════════════════════════════════════════════════════════════════
#  STEP 1 — GENERATE data.yaml
# ════════════════════════════════════════════════════════════════

def generate_data_yaml(output_path: Path = ROOT / "data.yaml") -> Path:
    """Generate YOLO-format data.yaml with all 100 class names."""
    names = [
        settings.ITEM_DISPLAY_NAME.get(k, k.replace("_", " ").title())
        for k in settings.CLASS_NAMES
    ]
    cfg = {
        "path":  str(DATASET.resolve()),
        "train": "images/train",
        "val":   "images/val",
        "test":  "images/test",
        "nc":    len(settings.CLASS_NAMES),
        "names": names,
    }
    with open(output_path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
    print(f"[✓] data.yaml written → {output_path}")
    print(f"    Classes: {cfg['nc']}")
    return output_path


# ════════════════════════════════════════════════════════════════
#  STEP 2 — VALIDATE dataset structure
# ════════════════════════════════════════════════════════════════

def validate_dataset():
    """Check dataset directory structure is correct for YOLO training."""
    required = [
        DATASET / "images" / "train",
        DATASET / "images" / "val",
        DATASET / "images" / "test",
        DATASET / "labels" / "train",
        DATASET / "labels" / "val",
        DATASET / "labels" / "test",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print("\n[!] MISSING DATASET DIRECTORIES:")
        for m in missing:
            print(f"    ✗  {m}")
        print("""
EXPECTED STRUCTURE:
  dataset/
  ├── images/
  │   ├── train/   ← 70% of images (35K–70K)
  │   ├── val/     ← 20% of images (10K–20K)
  │   └── test/    ← 10% of images  (5K–10K)
  └── labels/
      ├── train/   ← YOLO .txt annotations
      ├── val/
      └── test/

Each .txt label file format (one row per object):
  <class_id> <x_center> <y_center> <width> <height>
  All values normalized 0.0–1.0

DOWNLOAD OPTIONS:
  1. Roboflow  → https://universe.roboflow.com/  (search "e-waste")
  2. Open Images V7 → https://storage.googleapis.com/openimages/web/index.html
  3. Script   → run: python collect_dataset.py  (downloads from Roboflow API)
""")
        return False

    # Count images
    stats = {}
    total = 0
    for split in ["train", "val", "test"]:
        n = len(list((DATASET/"images"/split).glob("*.jpg")) +
                list((DATASET/"images"/split).glob("*.png")) +
                list((DATASET/"images"/split).glob("*.jpeg")))
        stats[split] = n
        total += n

    print(f"\n[✓] Dataset validated:")
    for split, n in stats.items():
        print(f"    {split:6s}: {n:,} images")
    print(f"    {'total':6s}: {total:,} images")

    if total < settings.DATASET_CONFIG["total_images_min"]:
        print(f"\n[⚠] WARNING: Only {total:,} images found. "
              f"Target: {settings.DATASET_CONFIG['total_images_min']:,}–"
              f"{settings.DATASET_CONFIG['total_images_max']:,}")
        print("    Model will still train but accuracy may be lower.")
    return True


# ════════════════════════════════════════════════════════════════
#  STEP 3 — TRAIN
# ════════════════════════════════════════════════════════════════

def train(
    data_yaml:   str  = "data.yaml",
    epochs:      int  = 300,
    batch:       int  = 16,
    imgsz:       int  = 640,
    device:      str  = "auto",
    resume:      bool = False,
    pretrained:  str  = "yolov8x.pt",
    dry_run:     bool = False,
):
    """Launch YOLOv8x training with full augmentation pipeline."""

    # Device selection
    if device == "auto":
        device = "0" if torch.cuda.is_available() else "cpu"

    if torch.cuda.is_available():
        gpu  = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"\n[GPU] {gpu}  {vram:.1f} GB VRAM")
        # Adjust batch for VRAM
        if vram < 8:
            batch = min(batch, 8)
            print(f"[!]  Low VRAM — batch adjusted to {batch}")
        elif vram < 16:
            batch = min(batch, 16)
    else:
        print("\n[CPU] No GPU found — training will be very slow.")
        print("      Consider Google Colab (free T4 GPU) for this dataset size.")
        batch = min(batch, 4)

    cfg = settings.TRAIN_CONFIG.copy()
    aug = settings.AUGMENTATION_CONFIG.copy()

    run_name = f"yolov8x_ewaste_{datetime.now().strftime('%Y%m%d_%H%M')}"

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  AI E-WASTE DETECTION — TRAINING CONFIG                      ║
╠══════════════════════════════════════════════════════════════╣
║  Model       : {pretrained:<46}║
║  Epochs      : {epochs:<46}║
║  Batch size  : {batch:<46}║
║  Image size  : {imgsz}×{imgsz:<42}║
║  Device      : {device:<46}║
║  Classes     : {len(settings.CLASS_NAMES):<46}║
║  Run name    : {run_name:<46}║
╚══════════════════════════════════════════════════════════════╝
""")

    if dry_run:
        print("[DRY RUN] Config validated. Pass --no-dry-run to start training.")
        return

    # Load base model
    print(f"[*] Loading base model: {pretrained}")
    model = YOLO(pretrained)

    # Start training
    results = model.train(
        data       = data_yaml,
        epochs     = epochs,
        batch      = batch,
        imgsz      = imgsz,
        device     = device,
        optimizer  = "AdamW",
        lr0        = 0.001,
        lrf        = 0.01,           # final LR = lr0 * lrf
        momentum   = 0.937,
        weight_decay = 0.0005,
        warmup_epochs = 3,
        warmup_bias_lr = 0.1,
        cos_lr     = True,
        patience   = 50,
        workers    = 8,
        cache      = True,
        rect       = False,
        resume     = resume,
        project    = str(RUNS),
        name       = run_name,
        exist_ok   = True,
        verbose    = True,
        plots      = True,
        save       = True,
        save_period = 10,
        val        = True,
        # Augmentation (matching spec)
        degrees    = aug["degrees"],
        translate  = aug["translate"],
        scale      = aug["scale"],
        shear      = aug["shear"],
        flipud     = aug["flipud"],
        fliplr     = aug["fliplr"],
        mosaic     = aug["mosaic"],
        mixup      = aug["mixup"],
        copy_paste = aug["copy_paste"],
        hsv_h      = aug["hsv_h"],
        hsv_s      = aug["hsv_s"],
        hsv_v      = aug["hsv_v"],
        erasing    = aug["erasing"],
    )

    # ── Post-training ─────────────────────────────────────────
    best_pt = list(RUNS.rglob("best.pt"))
    if best_pt:
        dst = WEIGHTS / "best.pt"
        shutil.copy2(best_pt[0], dst)
        print(f"\n[✓] Best model saved → {dst}")
    else:
        print("\n[!] best.pt not found in run directory")

    # Save training summary
    summary = {
        "timestamp":   datetime.now().isoformat(),
        "model":       pretrained,
        "run_name":    run_name,
        "epochs":      epochs,
        "batch":       batch,
        "imgsz":       imgsz,
        "device":      device,
        "num_classes": len(settings.CLASS_NAMES),
        "metrics":     {
            "map50":    float(getattr(results, 'box', {}).get('map50',   0)),
            "map50_95": float(getattr(results, 'box', {}).get('map',     0)),
            "precision":float(getattr(results, 'box', {}).get('mp',      0)),
            "recall":   float(getattr(results, 'box', {}).get('mr',      0)),
        }
    }
    summary_path = RUNS / f"{run_name}_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[✓] Training summary → {summary_path}")

    return results


# ════════════════════════════════════════════════════════════════
#  STEP 4 — VALIDATE / BENCHMARK
# ════════════════════════════════════════════════════════════════

def validate(model_path: str = "weights/best.pt", data_yaml: str = "data.yaml"):
    """Run validation on test set and print metrics."""
    p = Path(model_path)
    if not p.exists():
        print(f"[!] Model not found: {model_path}")
        return

    print(f"\n[*] Validating {model_path} on test split…")
    model   = YOLO(str(p))
    metrics = model.val(data=data_yaml, split="test", verbose=True, plots=True)

    map50    = metrics.box.map50
    map50_95 = metrics.box.map
    prec     = metrics.box.mp
    recall   = metrics.box.mr

    print(f"""
╔══════════════════════════════════════════════════════╗
║  VALIDATION RESULTS                                  ║
╠══════════════════════════════════════════════════════╣
║  mAP@50          : {map50:.4f}  {'✅' if map50>=0.95 else '⚠️ target 0.95'}{'':20}║
║  mAP@50-95       : {map50_95:.4f}  {'✅' if map50_95>=0.80 else '⚠️ target 0.80'}{'':20}║
║  Precision       : {prec:.4f}  {'✅' if prec>=0.92 else '⚠️ target 0.92'}{'':20}║
║  Recall          : {recall:.4f}  {'✅' if recall>=0.92 else '⚠️ target 0.92'}{'':20}║
╚══════════════════════════════════════════════════════╝
""")
    return metrics


# ════════════════════════════════════════════════════════════════
#  STEP 5 — EXPORT
# ════════════════════════════════════════════════════════════════

def export_model(model_path: str = "weights/best.pt", format: str = "onnx"):
    """Export trained model to ONNX/TensorRT/CoreML etc."""
    p = Path(model_path)
    if not p.exists():
        print(f"[!] Not found: {model_path}")
        return
    model = YOLO(str(p))
    path  = model.export(format=format, imgsz=640, simplify=True,
                          dynamic=False, opset=17)
    print(f"[✓] Exported → {path}")
    return path


# ════════════════════════════════════════════════════════════════
#  STEP 6 — DATASET STATS REPORT
# ════════════════════════════════════════════════════════════════

def dataset_stats():
    """Print per-class image count to identify imbalanced classes."""
    from collections import defaultdict
    counts = defaultdict(int)

    for split in ["train", "val", "test"]:
        label_dir = DATASET / "labels" / split
        if not label_dir.exists():
            continue
        for txt in label_dir.glob("*.txt"):
            for line in txt.read_text().strip().splitlines():
                parts = line.strip().split()
                if parts:
                    cls_id = int(parts[0])
                    counts[cls_id] += 1

    print(f"\n{'Class':30s} {'ID':5s} {'Count':>8s}  {'Status'}")
    print("-" * 65)
    total = 0
    under = 0
    for idx, name in enumerate(settings.CLASS_NAMES):
        n   = counts.get(idx, 0)
        total += n
        ok  = n >= settings.DATASET_CONFIG["images_per_class_min"]
        status = "✅ OK" if ok else f"⚠️  Need {settings.DATASET_CONFIG['images_per_class_min']-n} more"
        if not ok:
            under += 1
        display = settings.ITEM_DISPLAY_NAME.get(name, name)
        print(f"  {display:28s} {idx:5d} {n:>8,}  {status}")
    print("-" * 65)
    print(f"  {'TOTAL':28s} {'':5s} {total:>8,}")
    print(f"\n  Classes under minimum: {under}/{len(settings.CLASS_NAMES)}")


# ════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="AI E-Waste Detection — Training Pipeline"
    )
    subparsers = parser.add_subparsers(dest="cmd")

    # generate-yaml
    subparsers.add_parser("generate-yaml", help="Generate data.yaml")

    # validate-dataset
    subparsers.add_parser("validate-dataset", help="Check dataset structure")

    # stats
    subparsers.add_parser("stats", help="Per-class image counts")

    # train
    p_train = subparsers.add_parser("train", help="Start training")
    p_train.add_argument("--epochs",     type=int, default=300)
    p_train.add_argument("--batch",      type=int, default=16)
    p_train.add_argument("--imgsz",      type=int, default=640)
    p_train.add_argument("--device",     type=str, default="auto")
    p_train.add_argument("--model",      type=str, default="yolov8x.pt")
    p_train.add_argument("--data",       type=str, default="data.yaml")
    p_train.add_argument("--resume",     action="store_true")
    p_train.add_argument("--dry-run",    action="store_true")

    # validate
    p_val = subparsers.add_parser("validate", help="Validate trained model")
    p_val.add_argument("--model", type=str, default="weights/best.pt")
    p_val.add_argument("--data",  type=str, default="data.yaml")

    # export
    p_exp = subparsers.add_parser("export", help="Export model")
    p_exp.add_argument("--model",  type=str, default="weights/best.pt")
    p_exp.add_argument("--format", type=str, default="onnx",
                       choices=["onnx","tflite","coreml","engine","torchscript"])

    args = parser.parse_args()

    if args.cmd == "generate-yaml":
        generate_data_yaml()
    elif args.cmd == "validate-dataset":
        validate_dataset()
    elif args.cmd == "stats":
        dataset_stats()
    elif args.cmd == "train":
        yaml_path = generate_data_yaml()
        if validate_dataset() or args.dry_run:
            train(
                data_yaml  = str(yaml_path),
                epochs     = args.epochs,
                batch      = args.batch,
                imgsz      = args.imgsz,
                device     = args.device,
                resume     = args.resume,
                pretrained = args.model,
                dry_run    = args.dry_run,
            )
    elif args.cmd == "validate":
        validate(args.model, args.data)
    elif args.cmd == "export":
        export_model(args.model, args.format)
    else:
        # Default: show info
        print("""
╔══════════════════════════════════════════════════════════════════╗
║   AI E-WASTE OBJECT DETECTION — TRAINING PIPELINE               ║
╠══════════════════════════════════════════════════════════════════╣
║   Model     : YOLOv8x (swap to YOLOv9x for YOLOv9)             ║
║   Classes   : 100  (10 categories × 10 items each)              ║
║   Target    : 95–99% mAP@50                                     ║
╠══════════════════════════════════════════════════════════════════╣
║   COMMANDS:                                                      ║
║                                                                  ║
║   python train.py generate-yaml                                  ║
║     → Create data.yaml with all 100 class names                  ║
║                                                                  ║
║   python train.py validate-dataset                               ║
║     → Check dataset folder structure                             ║
║                                                                  ║
║   python train.py stats                                          ║
║     → Per-class image counts (find imbalanced classes)           ║
║                                                                  ║
║   python train.py train                                          ║
║     → Full training run (300 epochs, YOLOv8x)                   ║
║                                                                  ║
║   python train.py train --epochs 100 --dry-run                   ║
║     → Validate config without training                           ║
║                                                                  ║
║   python train.py validate --model weights/best.pt               ║
║     → Evaluate trained model on test set                         ║
║                                                                  ║
║   python train.py export --format onnx                           ║
║     → Export to ONNX for deployment                              ║
╚══════════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    main()
