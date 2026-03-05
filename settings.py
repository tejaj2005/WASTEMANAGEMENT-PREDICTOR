"""
Intelligent Waste Segregation System — Configuration & E-Waste Taxonomy
100-Class E-Waste Object Detection System
"""
from pathlib import Path
import os, sys
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

MODEL_DIR      = ROOT / "weights"
BEST_MODEL     = MODEL_DIR / "best.pt"
DATASET_DIR    = ROOT / "dataset"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WEBCAM_INDEX   = 0

# ══════════════════════════════════════════════════════════════════
#  100-CLASS E-WASTE TAXONOMY
#  10 Categories · ~100 classes · Target: 95–99% mAP
# ══════════════════════════════════════════════════════════════════

EWASTE_TAXONOMY = {

    # ── Category 1: Mobile Devices ────────────────────────────
    "mobile_devices": {
        "label":        "📱 Mobile Devices",
        "weee_cat":     "WEEE Cat 3 — IT & Telecom",
        "weee_code":    "WEEE/03",
        "hazard_level": "⚠️ Medium (lithium battery)",
        "recyclability":"High (conflict minerals: Ta, Co, Au)",
        "co2_per_kg":   40.0,
        "class_ids":    list(range(0, 10)),
        "items": {
            "smartphone":           "Smartphone",
            "feature_phone":        "Feature Phone",
            "tablet":               "Tablet",
            "smartwatch":           "Smartwatch",
            "fitness_band":         "Fitness Band",
            "mobile_battery":       "Mobile Battery",
            "mobile_back_cover":    "Mobile Back Cover",
            "mobile_screen":        "Mobile Screen",
            "mobile_motherboard":   "Mobile Motherboard",
            "sim_card_tray":        "SIM Card Tray",
        }
    },

    # ── Category 2: Computing Devices ─────────────────────────
    "computing_devices": {
        "label":        "💻 Computing Devices",
        "weee_cat":     "WEEE Cat 3 — IT & Telecom",
        "weee_code":    "WEEE/03",
        "hazard_level": "⚠️ Medium",
        "recyclability":"High (metals, plastics)",
        "co2_per_kg":   25.0,
        "class_ids":    list(range(10, 20)),
        "items": {
            "laptop":               "Laptop",
            "desktop_computer":     "Desktop Computer",
            "monitor":              "Monitor",
            "all_in_one_computer":  "All-in-One Computer",
            "mini_pc":              "Mini PC",
            "server_unit":          "Server Unit",
            "thin_client":          "Thin Client",
            "computer_cabinet":     "Computer Cabinet",
            "laptop_charger":       "Laptop Charger",
            "laptop_cooling_pad":   "Laptop Cooling Pad",
        }
    },

    # ── Category 3: Computer Peripherals ──────────────────────
    "peripherals": {
        "label":        "⌨️ Computer Peripherals",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "🟢 Low",
        "recyclability":"High (plastics, copper)",
        "co2_per_kg":   15.0,
        "class_ids":    list(range(20, 30)),
        "items": {
            "keyboard":             "Keyboard",
            "mouse":                "Mouse",
            "gaming_mouse":         "Gaming Mouse",
            "mechanical_keyboard":  "Mechanical Keyboard",
            "webcam":               "Webcam",
            "microphone":           "Microphone",
            "computer_speaker":     "Computer Speaker",
            "external_webcam":      "External Webcam",
            "graphics_tablet":      "Graphics Tablet",
            "barcode_scanner":      "Barcode Scanner",
        }
    },

    # ── Category 4: Storage Devices ───────────────────────────
    "storage_devices": {
        "label":        "💾 Storage Devices",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "⚠️ Medium (data security risk)",
        "recyclability":"High (metals, glass platters)",
        "co2_per_kg":   22.0,
        "class_ids":    list(range(30, 40)),
        "items": {
            "hard_disk_drive":      "Hard Disk Drive",
            "solid_state_drive":    "Solid State Drive",
            "external_hard_disk":   "External Hard Disk",
            "usb_flash_drive":      "USB Flash Drive",
            "memory_card":          "Memory Card",
            "micro_sd_card":        "Micro SD Card",
            "cd_disk":              "CD Disk",
            "dvd_disk":             "DVD Disk",
            "floppy_disk":          "Floppy Disk",
            "nas_storage_unit":     "NAS Storage Unit",
        }
    },

    # ── Category 5: Computer Components ───────────────────────
    "computer_components": {
        "label":        "🔧 Computer Components",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "🚨 High (PCB: lead, cadmium, beryllium)",
        "recyclability":"High (precious metals: Au, Ag, Cu, Pd)",
        "co2_per_kg":   35.0,
        "class_ids":    list(range(40, 50)),
        "items": {
            "motherboard":          "Motherboard",
            "cpu_processor":        "CPU Processor",
            "gpu":                  "GPU",
            "ram_module":           "RAM Module",
            "power_supply_unit":    "Power Supply Unit",
            "cooling_fan":          "Cooling Fan",
            "heat_sink":            "Heat Sink",
            "cmos_battery":         "CMOS Battery",
            "expansion_card":       "Expansion Card",
            "network_card":         "Network Card",
        }
    },

    # ── Category 6: Circuit Components ────────────────────────
    "circuit_components": {
        "label":        "⚡ Circuit Components",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "🚨 High (lead solder, rare earth metals)",
        "recyclability":"Medium (specialist smelting required)",
        "co2_per_kg":   50.0,
        "class_ids":    list(range(50, 60)),
        "items": {
            "pcb_board":            "PCB Board",
            "integrated_circuit":   "Integrated Circuit",
            "capacitor":            "Capacitor",
            "resistor":             "Resistor",
            "transistor":           "Transistor",
            "inductor":             "Inductor",
            "diode":                "Diode",
            "voltage_regulator":    "Voltage Regulator",
            "crystal_oscillator":   "Crystal Oscillator",
            "relay":                "Relay",
        }
    },

    # ── Category 7: Display Devices ───────────────────────────
    "display_devices": {
        "label":        "🖥️ Display Devices",
        "weee_cat":     "WEEE Cat 4 — Display Equipment",
        "weee_code":    "WEEE/04",
        "hazard_level": "🚨 High (mercury in CCFL, lead in CRT)",
        "recyclability":"Medium (specialized processing)",
        "co2_per_kg":   30.0,
        "class_ids":    list(range(60, 70)),
        "items": {
            "lcd_panel":            "LCD Panel",
            "led_panel":            "LED Panel",
            "crt_monitor":          "CRT Monitor",
            "television":           "Television",
            "smart_tv":             "Smart TV",
            "projector":            "Projector",
            "projector_lens":       "Projector Lens",
            "display_controller_board": "Display Controller Board",
            "tv_remote":            "TV Remote",
            "led_driver_board":     "LED Driver Board",
        }
    },

    # ── Category 8: Audio Devices ──────────────────────────────
    "audio_devices": {
        "label":        "🎵 Audio Devices",
        "weee_cat":     "WEEE Cat 2 — AV Equipment",
        "weee_code":    "WEEE/02",
        "hazard_level": "🟢 Low",
        "recyclability":"Medium (mixed materials)",
        "co2_per_kg":   20.0,
        "class_ids":    list(range(70, 80)),
        "items": {
            "headphones":           "Headphones",
            "earphones":            "Earphones",
            "bluetooth_headset":    "Bluetooth Headset",
            "wireless_earbuds":     "Wireless Earbuds",
            "soundbar":             "Soundbar",
            "subwoofer":            "Subwoofer",
            "amplifier":            "Amplifier",
            "audio_receiver":       "Audio Receiver",
            "audio_microphone":     "Microphone",
            "dj_controller":        "DJ Controller",
        }
    },

    # ── Category 9: Networking Devices ────────────────────────
    "networking_devices": {
        "label":        "📡 Networking Devices",
        "weee_cat":     "WEEE Cat 3 — IT & Telecom",
        "weee_code":    "WEEE/03",
        "hazard_level": "🟢 Low",
        "recyclability":"High (metals, PCB)",
        "co2_per_kg":   18.0,
        "class_ids":    list(range(80, 90)),
        "items": {
            "wifi_router":          "WiFi Router",
            "network_switch":       "Network Switch",
            "modem":                "Modem",
            "lan_cable":            "LAN Cable",
            "ethernet_connector":   "Ethernet Connector",
            "network_antenna":      "Network Antenna",
            "access_point":         "Access Point",
            "signal_booster":       "Signal Booster",
            "fiber_converter":      "Fiber Converter",
            "network_hub":          "Network Hub",
        }
    },

    # ── Category 10: Power Devices ────────────────────────────
    "power_devices": {
        "label":        "🔋 Power Devices",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "🚨 High (acid, lithium fire risk)",
        "recyclability":"High (lead, lithium, cobalt recovery)",
        "co2_per_kg":   28.0,
        "class_ids":    list(range(90, 100)),
        "items": {
            "battery":              "Battery",
            "lithium_battery":      "Lithium Battery",
            "power_adapter":        "Power Adapter",
            "charger":              "Charger",
            "ups":                  "UPS",
            "inverter":             "Inverter",
            "power_bank":           "Power Bank",
            "extension_board":      "Extension Board",
            "power_cable":          "Power Cable",
            "adapter_plug":         "Adapter Plug",
        }
    },
}

# ══════════════════════════════════════════════════════════════════
#  FLAT LOOKUP TABLES  (auto-built from taxonomy)
# ══════════════════════════════════════════════════════════════════
ITEM_SUBCATEGORY:   dict = {}
ITEM_DISPLAY_NAME:  dict = {}
ITEM_WEEE_CAT:      dict = {}
ITEM_WEEE_CODE:     dict = {}
ITEM_HAZARD:        dict = {}
ITEM_RECYCLABILITY: dict = {}
ITEM_CO2_PER_KG:    dict = {}
SUBCATEGORY_LABELS: dict = {}

# Class ID → item key (ordered list — index = class ID)
CLASS_NAMES: list = []

for _subcat_key, _meta in EWASTE_TAXONOMY.items():
    SUBCATEGORY_LABELS[_subcat_key] = _meta["label"]
    for _item_key, _display in _meta["items"].items():
        ITEM_SUBCATEGORY[_item_key]   = _subcat_key
        ITEM_DISPLAY_NAME[_item_key]  = _display
        ITEM_WEEE_CAT[_item_key]      = _meta["weee_cat"]
        ITEM_WEEE_CODE[_item_key]     = _meta["weee_code"]
        ITEM_HAZARD[_item_key]        = _meta["hazard_level"]
        ITEM_RECYCLABILITY[_item_key] = _meta["recyclability"]
        ITEM_CO2_PER_KG[_item_key]    = _meta["co2_per_kg"]
        CLASS_NAMES.append(_item_key)

# Reverse: item_key → class_id
CLASS_ID: dict = {name: idx for idx, name in enumerate(CLASS_NAMES)}

# All E-waste items (flat)
EWASTE_ALL: list = CLASS_NAMES.copy()

# ══════════════════════════════════════════════════════════════════
#  WASTE CLASSIFICATION (for detection labelling)
# ══════════════════════════════════════════════════════════════════
# All e-waste items are recyclable (via specialist facilities)
# Some are additionally flagged hazardous
RECYCLABLE:     list = EWASTE_ALL + [
    "cardboard_box", "can", "plastic_bottle_cap", "plastic_bottle",
    "reuseable_paper", "paper", "cardboard", "aluminum",
    "glass_bottle", "metal_can", "plastic", "newspaper", "magazine",
]

NON_RECYCLABLE: list = [
    "plastic_bag", "scrap_paper", "stick", "plastic_cup", "snack_bag",
    "plastic_box", "straw", "plastic_cup_lid", "scrap_plastic",
    "cardboard_bowl", "plastic_cultery", "foam", "styrofoam",
    "tissue", "napkin", "food_waste", "organic_waste",
]

HAZARDOUS: list = [
    # Items with high hazard in taxonomy
    "mobile_battery", "mobile_motherboard",
    "motherboard", "gpu", "cpu_processor", "cmos_battery",
    "pcb_board", "integrated_circuit", "capacitor",
    "transistor", "inductor", "diode", "voltage_regulator",
    "crt_monitor", "lcd_panel", "led_driver_board", "display_controller_board",
    "battery", "lithium_battery", "ups", "inverter",
    # General hazardous
    "chemical_spray_can", "chemical_plastic_bottle",
    "chemical_plastic_gallon", "paint_bucket", "medical_waste",
    "broken_glass", "sharp_objects", "light_bulb",
]

# ══════════════════════════════════════════════════════════════════
#  COCO CLASS → E-WASTE MAPPING
#  (for general YOLO models detecting COCO classes)
# ══════════════════════════════════════════════════════════════════
COCO_TO_EWASTE: dict = {
    "laptop":       "laptop",
    "cell phone":   "smartphone",
    "tv":           "television",
    "keyboard":     "keyboard",
    "mouse":        "mouse",
    "remote":       "tv_remote",
    "microwave":    "desktop_computer",
    "bottle":       "plastic_bottle",
    "cup":          "plastic_cup",
    "scissors":     "sharp_objects",
}

# ══════════════════════════════════════════════════════════════════
#  TRAINING CONFIGURATION CONSTANTS
# ══════════════════════════════════════════════════════════════════
TRAIN_CONFIG = {
    "model":         "yolov8x.pt",         # largest YOLOv8 for max accuracy
    "epochs":        300,
    "batch":         16,
    "imgsz":         640,
    "lr0":           0.001,
    "optimizer":     "AdamW",
    "patience":      50,                   # early stop if no improvement
    "workers":       8,
    "cache":         True,
    "rect":          False,
    "cos_lr":        True,                 # cosine LR schedule
    "warmup_epochs": 3,
    "save_period":   10,                   # save checkpoint every N epochs
    "device":        "0",                  # GPU 0; use 'cpu' if no GPU
    "project":       "runs/ewaste",
    "name":          "yolov8x_ewaste_v1",
    "exist_ok":      True,
    "verbose":       True,
    "plots":         True,
    "val":           True,
    # Target metrics
    "target_map50":  0.95,
    "target_map50_95": 0.80,
}

AUGMENTATION_CONFIG = {
    # Geometric
    "degrees":    10.0,    # rotation ±10°
    "translate":  0.1,     # translate ±10%
    "scale":      0.5,     # scale ±50%
    "shear":      2.0,     # shear ±2°
    "flipud":     0.1,     # vertical flip prob
    "fliplr":     0.5,     # horizontal flip prob
    "mosaic":     1.0,     # mosaic augmentation
    "mixup":      0.15,    # mixup augmentation
    "copy_paste": 0.1,     # copy-paste augmentation
    # Color
    "hsv_h":      0.015,   # hue shift
    "hsv_s":      0.7,     # saturation shift
    "hsv_v":      0.4,     # value/brightness shift
    # Quality
    "erasing":    0.4,     # random erasing prob
    "blur":       0.02,    # blur prob
}

DATASET_CONFIG = {
    "images_per_class_min":  500,
    "images_per_class_max":  1200,
    "total_images_min":      50_000,
    "total_images_max":      100_000,
    "train_split":           0.70,
    "val_split":             0.20,
    "test_split":            0.10,
    "image_size":            640,
    "num_classes":           100,
}
