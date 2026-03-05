"""
Automated Dataset Collection for AI E-Waste Detection System
Downloads and organizes datasets for all 100 classes from:
  1. Roboflow Universe (primary — best annotated)
  2. Open Images V7   (secondary — large scale)
  3. Google Images    (tertiary — fill gaps)

Usage:
  python collect_dataset.py --source roboflow  --api-key YOUR_KEY
  python collect_dataset.py --source openimages
  python collect_dataset.py --source all       --api-key YOUR_KEY
  python collect_dataset.py --check            (just verify structure)
"""
import os, sys, shutil, json, csv, random, argparse
from pathlib import Path
from datetime import datetime

ROOT    = Path(__file__).parent
DATASET = ROOT / "dataset"

# ── Ensure deps ───────────────────────────────────────────────
def _install(pkg):
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

try:
    import yaml
except ImportError:
    _install("pyyaml"); import yaml

try:
    import requests
except ImportError:
    _install("requests"); import requests

# ════════════════════════════════════════════════════════════════
#  ROBOFLOW DATASET MAPPINGS
#  Pre-curated public datasets on Roboflow Universe
#  that map well to our 100-class taxonomy
# ════════════════════════════════════════════════════════════════

ROBOFLOW_DATASETS = [
    # (workspace, project, version, description)
    ("roboflow-100",    "e-waste-detection-2",       1, "E-waste general"),
    ("roboflow-100",    "circuit-board-defect",      1, "PCB / circuit boards"),
    ("roboflow-100",    "electronic-components",     1, "Small components"),
    ("richa-1cxke",     "e-waste-detection-system",  1, "E-waste system"),
    ("e-waste-dataset", "e-waste-xvlte",             1, "E-waste items"),
    ("waste-detection", "waste-detection-v2",        1, "Waste categories"),
    ("techscrap",       "computer-parts-detection",  1, "Computer parts"),
    ("pcb-dataset",     "pcb-board-detection",       2, "PCB boards"),
    ("battery-detect",  "battery-type-detection",    1, "Battery types"),
    ("phone-recycle",   "phone-component-detection", 1, "Phone components"),
]

# Open Images classes that map to our 100 taxonomy classes
OPEN_IMAGES_CLASSES = [
    # Mobile Devices
    "Mobile phone", "Tablet computer", "Smartphone",
    # Computing
    "Laptop", "Desktop computer", "Computer monitor",
    # Peripherals
    "Computer keyboard", "Computer mouse",
    # Storage
    "Hard disk drive",
    # Display
    "Television", "Projector",
    # Audio
    "Headphones", "Earphones", "Microphone",
    # Networking
    "Router",
    # Power
    "Battery charger",
]

# ── CLASS NAME → our taxonomy ID ─────────────────────────────
# Maps common Roboflow class names → our canonical IDs
CLASS_REMAP = {
    # Mobile
    "phone":                0, "mobile phone":         0, "smartphone":          0,
    "feature phone":        1, "keypad phone":         1,
    "tablet":               2, "ipad":                 2, "tablet computer":     2,
    "smartwatch":           3, "apple watch":          3, "watch":               3,
    "fitness band":         4, "fitness tracker":      4, "wristband":           4,
    "mobile battery":       5, "phone battery":        5, "battery pack":        5,
    "phone case":           6, "back cover":           6, "phone cover":         6,
    "phone screen":         7, "phone display":        7, "mobile screen":       7,
    "phone motherboard":    8, "phone pcb":            8,
    "sim tray":             9, "sim card tray":        9,
    # Computing
    "laptop":              10, "notebook":             10, "macbook":            10,
    "desktop":             11, "desktop computer":    11, "pc":                 11,
    "monitor":             12, "computer monitor":    12, "lcd monitor":        12,
    "all in one":          13, "all-in-one":          13, "aio":                13,
    "mini pc":             14, "nuc":                 14,
    "server":              15, "server unit":         15, "rack server":        15,
    "thin client":         16,
    "computer case":       17, "pc case":             17, "tower case":         17,
    "laptop charger":      18, "laptop adapter":      18, "power brick":        18,
    "cooling pad":         19, "laptop cooler":       19,
    # Peripherals
    "keyboard":            20,
    "mouse":               21, "computer mouse":      21,
    "gaming mouse":        22,
    "mechanical keyboard": 23,
    "webcam":              24, "web camera":          24,
    "microphone":          25, "mic":                 25, "blue yeti":          25,
    "speaker":             26, "computer speaker":    26, "pc speaker":         26,
    "external webcam":     27,
    "graphics tablet":     28, "drawing tablet":      28, "wacom":              28,
    "barcode scanner":     29, "scanner":             29,
    # Storage
    "hard disk":           30, "hdd":                 30, "hard disk drive":    30,
    "ssd":                 31, "solid state drive":   31, "solid-state drive":  31,
    "external hard disk":  32, "external hdd":        32,
    "usb":                 33, "usb drive":           33, "flash drive":        33, "pendrive": 33,
    "memory card":         34, "sd card":             34, "cf card":            34,
    "micro sd":            35, "microsd":             35,
    "cd":                  36, "cd disk":             36, "compact disc":       36,
    "dvd":                 37, "dvd disk":            37,
    "floppy disk":         38, "floppy":              38,
    "nas":                 39, "nas storage":         39,
    # Components
    "motherboard":         40, "mainboard":           40, "mobo":               40,
    "cpu":                 41, "processor":           41, "cpu chip":           41,
    "gpu":                 42, "graphics card":       42, "video card":         42,
    "ram":                 43, "memory":              43, "ram module":         43, "dimm": 43,
    "psu":                 44, "power supply":        44, "power supply unit":  44,
    "fan":                 45, "cooling fan":         45, "case fan":           45,
    "heat sink":           46, "heatsink":            46, "cooler":             46,
    "cmos":                47, "cmos battery":        47, "coin battery":       47,
    "expansion card":      48, "pcie card":           48, "add-in card":        48,
    "network card":        49, "nic":                 49, "lan card":           49,
    # Circuit
    "pcb":                 50, "pcb board":           50, "circuit board":      50, "green board": 50,
    "ic":                  51, "integrated circuit":  51, "chip":               51,
    "capacitor":           52, "cap":                 52,
    "resistor":            53,
    "transistor":          54,
    "inductor":            55, "coil":                55,
    "diode":               56, "led":                 56,
    "voltage regulator":   57, "ldo":                 57,
    "crystal oscillator":  58, "crystal":             58,
    "relay":               59,
    # Display
    "lcd panel":           60, "lcd":                 60, "lcd screen":         60,
    "led panel":           61, "led display":         61,
    "crt":                 62, "crt monitor":         62, "crt television":     62,
    "tv":                  63, "television":          63, "television set":     63,
    "smart tv":            64, "smart television":    64, "android tv":         64,
    "projector":           65,
    "projector lens":      66, "lens":                66,
    "display board":       67, "t-con board":         67, "display controller": 67,
    "remote":              68, "remote control":      68, "tv remote":          68,
    "led driver":          69, "led driver board":    69,
    # Audio
    "headphones":          70, "over-ear":            70, "headset":            70,
    "earphones":           71, "earphone":            71, "in-ear":             71,
    "bluetooth headset":   72, "bt headset":          72,
    "earbuds":             73, "wireless earbuds":    73, "tws":                73,
    "soundbar":            74, "sound bar":           74,
    "subwoofer":           75, "woofer":              75,
    "amplifier":           76, "amp":                 76, "audio amp":          76,
    "audio receiver":      77, "av receiver":         77, "receiver":           77,
    "audio microphone":    78,
    "dj controller":       79, "dj":                  79,
    # Networking
    "router":              80, "wifi router":         80, "wireless router":    80,
    "switch":              81, "network switch":      81, "ethernet switch":    81,
    "modem":               82, "cable modem":         82,
    "lan cable":           83, "ethernet cable":      83, "rj45 cable":         83,
    "ethernet connector":  84, "rj45":                84, "ethernet port":      84,
    "antenna":             85, "wifi antenna":        85, "network antenna":    85,
    "access point":        86, "ap":                  86, "wireless ap":        86,
    "signal booster":      87, "repeater":            87, "range extender":     87,
    "fiber converter":     88, "media converter":     88,
    "hub":                 89, "network hub":         89, "ethernet hub":       89,
    # Power
    "battery":             90, "lead acid battery":   90, "aa battery":         90,
    "lithium battery":     91, "lithium ion":         91, "li-ion battery":     91,
    "power adapter":       92, "ac adapter":          92, "wall adapter":       92,
    "charger":             93, "phone charger":       93, "usb charger":        93,
    "ups":                 94, "uninterruptible":     94,
    "inverter":            95, "power inverter":      95,
    "power bank":          96, "portable charger":    96,
    "extension board":     97, "extension cord":      97, "power strip":        97,
    "power cable":         98, "power cord":          98, "iec cable":          98,
    "adapter plug":        99, "plug adapter":        99, "travel adapter":    99,
}


# ════════════════════════════════════════════════════════════════
#  DATASET STRUCTURE
# ════════════════════════════════════════════════════════════════

def create_structure():
    for split in ["train", "val", "test"]:
        (DATASET / "images" / split).mkdir(parents=True, exist_ok=True)
        (DATASET / "labels" / split).mkdir(parents=True, exist_ok=True)
    print("[✓] Dataset directory structure created")


def check_structure():
    """Print current dataset status."""
    print("\n📁 Dataset Status")
    print("=" * 60)
    total_images = 0
    total_labels = 0
    for split in ["train", "val", "test"]:
        img_dir = DATASET / "images" / split
        lbl_dir = DATASET / "labels" / split
        imgs = len(list(img_dir.glob("*.[jJpP][pPnN][gGgG]"))) if img_dir.exists() else 0
        lbls = len(list(lbl_dir.glob("*.txt")))                 if lbl_dir.exists() else 0
        total_images += imgs
        total_labels += lbls
        status = "✅" if imgs > 0 else "❌"
        print(f"  {status} {split:6s}:  {imgs:>7,} images  {lbls:>7,} labels")
    print(f"  {'':8s}  {total_images:>7,} total   {total_labels:>7,} total")

    if total_images == 0:
        print("""
⚠️  No images found. Options to populate:

  A) Roboflow (easiest):
     python collect_dataset.py --source roboflow --api-key YOUR_KEY

  B) Open Images (free, no key):
     python collect_dataset.py --source openimages

  C) Manual:
     1. Go to https://universe.roboflow.com/
     2. Search: "e-waste" / "circuit board" / "electronic components"
     3. Download in YOLOv8 format
     4. Place images in dataset/images/train|val|test/
     5. Place labels in dataset/labels/train|val|test/
""")
    return total_images


# ════════════════════════════════════════════════════════════════
#  SOURCE 1 — ROBOFLOW
# ════════════════════════════════════════════════════════════════

def download_roboflow(api_key: str):
    """Download curated e-waste datasets from Roboflow Universe."""
    try:
        from roboflow import Roboflow
    except ImportError:
        _install("roboflow")
        from roboflow import Roboflow

    print("\n🌐 Downloading from Roboflow Universe…")
    rf  = Roboflow(api_key=api_key)
    ok  = 0
    fail = 0

    for workspace, project, version, desc in ROBOFLOW_DATASETS:
        try:
            print(f"\n  → {desc}  ({workspace}/{project} v{version})")
            proj   = rf.workspace(workspace).project(project)
            ds     = proj.version(version).download("yolov8", location=str(DATASET/"tmp"))
            _import_roboflow_download(DATASET / "tmp", desc)
            shutil.rmtree(DATASET / "tmp", ignore_errors=True)
            ok += 1
            print(f"    ✅ Done")
        except Exception as e:
            fail += 1
            print(f"    ⚠️  Skipped: {e}")

    print(f"\n[Roboflow] {ok} datasets downloaded, {fail} skipped")
    return ok


def _import_roboflow_download(src: Path, name: str):
    """Copy Roboflow download into our dataset/ structure with class remapping."""
    for split in ["train", "valid", "test"]:
        split_key = "val" if split == "valid" else split
        img_src = src / split / "images"
        lbl_src = src / split / "labels"

        if not img_src.exists():
            continue

        img_dst = DATASET / "images" / split_key
        lbl_dst = DATASET / "labels" / split_key

        # Copy and remap labels
        for img_file in img_src.glob("*.[jJpP][pPnN][gGgG]"):
            stem    = img_file.stem
            lbl_file = lbl_src / f"{stem}.txt"
            # Unique name to avoid collision
            uid     = f"{name.replace(' ','_')}_{img_file.name}"
            shutil.copy2(img_file, img_dst / uid)

            if lbl_file.exists():
                remapped = _remap_labels(lbl_file, src / "data.yaml")
                if remapped:
                    (lbl_dst / f"{name.replace(' ','_')}_{stem}.txt").write_text(remapped)


def _remap_labels(label_file: Path, data_yaml_path: Path) -> str:
    """Remap class IDs from source dataset to our 100-class taxonomy."""
    # Load source class names
    src_names = {}
    if data_yaml_path.exists():
        with open(data_yaml_path) as f:
            src_cfg   = yaml.safe_load(f)
            src_names = {i: n.lower() for i, n in enumerate(src_cfg.get("names", []))}

    lines_out = []
    for line in label_file.read_text().strip().splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        src_id  = int(parts[0])
        src_cls = src_names.get(src_id, "")
        # Lookup in remap table
        our_id  = CLASS_REMAP.get(src_cls, CLASS_REMAP.get(src_cls.lower()))
        if our_id is not None:
            lines_out.append(f"{our_id} {' '.join(parts[1:])}")
        # else: skip unknown classes
    return "\n".join(lines_out)


# ════════════════════════════════════════════════════════════════
#  SOURCE 2 — OPEN IMAGES V7
# ════════════════════════════════════════════════════════════════

def download_openimages(max_per_class: int = 500):
    """Download from Open Images V7 using FiftyOne."""
    try:
        import fiftyone as fo
        import fiftyone.zoo as foz
    except ImportError:
        _install("fiftyone")
        import fiftyone as fo
        import fiftyone.zoo as foz

    print("\n🌐 Downloading from Open Images V7…")

    # Map OI classes → our IDs
    OI_MAP = {
        "Mobile phone":         0,
        "Tablet computer":      2,
        "Laptop":              10,
        "Desktop computer":    11,
        "Computer monitor":    12,
        "Computer keyboard":   20,
        "Computer mouse":      21,
        "Microphone":          25,
        "Headphones":          70,
        "Television":          63,
        "Projector":           65,
        "Router":              80,
    }

    for oi_class, our_id in OI_MAP.items():
        try:
            print(f"  → {oi_class} (ID {our_id}) — {max_per_class} images")
            dataset = foz.load_zoo_dataset(
                "open-images-v7",
                split="train",
                label_types=["detections"],
                classes=[oi_class],
                max_samples=max_per_class,
                dataset_name=f"oi_{our_id}_{oi_class.replace(' ','_').lower()}",
            )
            _export_fiftyone(dataset, our_id, oi_class)
            fo.delete_dataset(dataset.name)
            print(f"    ✅ Done")
        except Exception as e:
            print(f"    ⚠️  Skipped {oi_class}: {e}")


def _export_fiftyone(dataset, our_id: int, class_name: str):
    """Export FiftyOne dataset into our YOLO structure."""
    import fiftyone as fo

    for sample in dataset:
        img_path = Path(sample.filepath)
        if not img_path.exists():
            continue

        w   = sample.metadata.width  if sample.metadata else 640
        h   = sample.metadata.height if sample.metadata else 640

        lines = []
        dets  = sample.ground_truth.detections if sample.ground_truth else []
        for det in dets:
            bx, by, bw, bh = det.bounding_box  # [x, y, w, h] in [0,1]
            cx = bx + bw / 2
            cy = by + bh / 2
            lines.append(f"{our_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")

        if not lines:
            continue

        # Random split 70/20/10
        r     = random.random()
        split = "train" if r < 0.7 else ("val" if r < 0.9 else "test")
        uid   = f"oi_{our_id}_{img_path.name}"

        shutil.copy2(img_path, DATASET / "images" / split / uid)
        (DATASET / "labels" / split / f"oi_{our_id}_{img_path.stem}.txt").write_text(
            "\n".join(lines)
        )


# ════════════════════════════════════════════════════════════════
#  SOURCE 3 — GOOGLE IMAGES (gap-fill, no bbox labels)
#  Downloaded images go to raw_images/ for manual annotation
# ════════════════════════════════════════════════════════════════

def download_google_images(classes_to_fill: list, per_class: int = 200):
    """
    Download images from Google for classes still under minimum.
    NOTE: These need manual annotation before training.
    """
    try:
        from icrawler.builtin import GoogleImageCrawler
    except ImportError:
        _install("icrawler")
        from icrawler.builtin import GoogleImageCrawler

    RAW = ROOT / "raw_images_to_annotate"
    RAW.mkdir(exist_ok=True)
    print(f"\n📷 Google image collection → {RAW}")
    print("  ⚠️  These need annotation before use in training!")

    import settings
    for idx in classes_to_fill:
        name = settings.ITEM_DISPLAY_NAME.get(settings.CLASS_NAMES[idx], str(idx))
        out  = RAW / f"{idx:03d}_{name.replace(' ','_')}"
        out.mkdir(exist_ok=True)
        print(f"  Crawling: {name} ({per_class} images)…")
        try:
            query = f"{name} e-waste recycling electronics"
            GoogleImageCrawler(
                storage={"root_dir": str(out)},
                feeder_threads=1, parser_threads=1, downloader_threads=4
            ).crawl(keyword=query, max_num=per_class,
                    file_idx_offset="auto")
        except Exception as e:
            print(f"    ⚠️  {e}")

    print(f"\n[✓] Raw images saved to: {RAW}")
    print("  Next: Annotate with Roboflow Annotate (free) or CVAT")
    print("  Upload URL: https://app.roboflow.com/")


# ════════════════════════════════════════════════════════════════
#  SPLIT EXISTING IMAGES (if you have an un-split folder)
# ════════════════════════════════════════════════════════════════

def split_dataset(source_dir: str, train=0.70, val=0.20):
    """Split a flat folder of annotated images into train/val/test."""
    src  = Path(source_dir)
    imgs = list(src.glob("*.[jJpP][pPnN][gGgG]"))
    if not imgs:
        print(f"No images in {src}")
        return

    random.shuffle(imgs)
    n     = len(imgs)
    n_tr  = int(n * train)
    n_val = int(n * val)

    splits = {
        "train": imgs[:n_tr],
        "val":   imgs[n_tr:n_tr+n_val],
        "test":  imgs[n_tr+n_val:],
    }

    create_structure()
    for split, files in splits.items():
        for img in files:
            shutil.copy2(img, DATASET / "images" / split / img.name)
            lbl = img.parent / "labels" / f"{img.stem}.txt"
            if not lbl.exists():
                lbl = img.with_suffix(".txt")
            if lbl.exists():
                shutil.copy2(lbl, DATASET / "labels" / split / lbl.name)

    print(f"[✓] Split {n} images → train:{len(splits['train'])} "
          f"val:{len(splits['val'])} test:{len(splits['test'])}")


# ════════════════════════════════════════════════════════════════
#  GENERATE PROGRESS REPORT
# ════════════════════════════════════════════════════════════════

def generate_report():
    """Generate a detailed CSV report of dataset status per class."""
    import settings
    from collections import defaultdict

    counts = defaultdict(int)
    for split in ["train", "val", "test"]:
        lbl_dir = DATASET / "labels" / split
        if not lbl_dir.exists():
            continue
        for txt in lbl_dir.glob("*.txt"):
            for line in txt.read_text().strip().splitlines():
                parts = line.strip().split()
                if parts:
                    counts[int(parts[0])] += 1

    report_path = ROOT / "dataset_report.csv"
    TARGET = settings.DATASET_CONFIG["images_per_class_min"]
    with open(report_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Class", "Category", "Count", "Target",
                    "Gap", "% Complete", "Status"])
        for idx, key in enumerate(settings.CLASS_NAMES):
            subcat = settings.ITEM_SUBCATEGORY.get(key, "")
            label  = settings.SUBCATEGORY_LABELS.get(subcat, "General")
            name   = settings.ITEM_DISPLAY_NAME.get(key, key)
            n      = counts[idx]
            gap    = max(0, TARGET - n)
            pct    = min(100, int(n / TARGET * 100))
            status = "READY" if n >= TARGET else ("PARTIAL" if n > 0 else "EMPTY")
            w.writerow([idx, name, label, n, TARGET, gap, f"{pct}%", status])

    print(f"\n[✓] Dataset report → {report_path}")

    # Summary
    ready   = sum(1 for i in range(len(settings.CLASS_NAMES))
                  if counts[i] >= TARGET)
    partial = sum(1 for i in range(len(settings.CLASS_NAMES))
                  if 0 < counts[i] < TARGET)
    empty   = len(settings.CLASS_NAMES) - ready - partial

    print(f"""
  📊 Status Summary:
    ✅ READY   : {ready:3d}/{len(settings.CLASS_NAMES)} classes (≥{TARGET} images)
    ⚠️  PARTIAL : {partial:3d}/{len(settings.CLASS_NAMES)} classes (>0 but <{TARGET})
    ❌ EMPTY   : {empty:3d}/{len(settings.CLASS_NAMES)} classes (0 images)
""")
    return report_path


# ════════════════════════════════════════════════════════════════
#  CLI
# ════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="E-Waste Dataset Collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Check current status
  python collect_dataset.py --check

  # Download from Roboflow (needs free API key)
  python collect_dataset.py --source roboflow --api-key YOUR_ROBOFLOW_KEY

  # Download from Open Images (no key needed)
  python collect_dataset.py --source openimages --max-per-class 500

  # Fill gaps with Google Images (manual annotation needed)
  python collect_dataset.py --source google --max-per-class 200

  # Download from all sources
  python collect_dataset.py --source all --api-key YOUR_ROBOFLOW_KEY

  # Split an existing annotated folder into train/val/test
  python collect_dataset.py --split /path/to/my_annotated_images

  # Generate CSV progress report
  python collect_dataset.py --report

GET ROBOFLOW API KEY (FREE):
  1. Register at https://app.roboflow.com/
  2. Go to Settings → API Keys
  3. Copy your Private API Key
""")

    parser.add_argument("--source",       choices=["roboflow","openimages","google","all"],
                        help="Data source")
    parser.add_argument("--api-key",      type=str, default="",
                        help="Roboflow API key (free at app.roboflow.com)")
    parser.add_argument("--max-per-class",type=int, default=500,
                        help="Max images per class (default 500)")
    parser.add_argument("--check",        action="store_true",
                        help="Just show dataset status")
    parser.add_argument("--split",        type=str, default="",
                        help="Split an existing folder into train/val/test")
    parser.add_argument("--report",       action="store_true",
                        help="Generate per-class CSV report")

    args = parser.parse_args()

    create_structure()

    if args.check:
        check_structure()
        return

    if args.report:
        generate_report()
        return

    if args.split:
        split_dataset(args.split)
        return

    if not args.source:
        parser.print_help()
        print("\n--- Current dataset status ---")
        check_structure()
        return

    if args.source in ("roboflow", "all"):
        if not args.api_key:
            print("""
❌ Roboflow API key required!

  Get a FREE key at: https://app.roboflow.com/ → Settings → API Keys

  Then run:
    python collect_dataset.py --source roboflow --api-key YOUR_KEY
""")
        else:
            download_roboflow(args.api_key)

    if args.source in ("openimages", "all"):
        download_openimages(max_per_class=args.max_per_class)

    if args.source in ("google", "all"):
        import settings
        from collections import defaultdict
        counts = defaultdict(int)
        for split in ["train","val","test"]:
            lbl_dir = DATASET / "labels" / split
            if lbl_dir.exists():
                for txt in lbl_dir.glob("*.txt"):
                    for line in txt.read_text().strip().splitlines():
                        parts = line.strip().split()
                        if parts: counts[int(parts[0])] += 1
        MIN = settings.DATASET_CONFIG["images_per_class_min"]
        empty_classes = [i for i in range(len(settings.CLASS_NAMES))
                         if counts[i] < MIN]
        download_google_images(empty_classes, per_class=args.max_per_class)

    # Final status
    check_structure()
    generate_report()
    print("\n✅ Done! Next steps:")
    print("  1. python train.py stats             ← verify per-class counts")
    print("  2. python train.py validate-dataset  ← confirm structure")
    print("  3. python train.py train             ← start training!")


if __name__ == "__main__":
    main()
