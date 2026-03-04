"""
Intelligent Waste Segregation System — Configuration & E-Waste Taxonomy
"""
from pathlib import Path
import os, sys
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

MODEL_DIR       = ROOT / "weights"
BEST_MODEL      = MODEL_DIR / "best.pt"
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
WEBCAM_INDEX    = 0

# ══════════════════════════════════════════════════════════════════
#  COMPREHENSIVE E-WASTE TAXONOMY
#  WEEE — Waste Electrical & Electronic Equipment Directive
# ══════════════════════════════════════════════════════════════════
EWASTE_TAXONOMY = {

    # ── WEEE Cat 3: IT & Telecommunications Equipment ──────────
    "computing_devices": {
        "label":        "💻 Computing Devices",
        "weee_cat":     "WEEE Cat 3 — IT & Telecom",
        "weee_code":    "WEEE/03",
        "hazard_level": "⚠️ Medium",
        "recyclability":"High (metals, plastics)",
        "co2_per_kg":   25.0,   # kg CO2 saved per kg recycled
        "items": {
            "laptop":               "Laptop / Notebook",
            "desktop_cpu":          "Desktop PC (Tower)",
            "all_in_one_pc":        "All-in-One PC",
            "server_rack":          "Server / Rack Unit",
            "workstation":          "Workstation PC",
            "tablet":               "Tablet / iPad",
            "chromebook":           "Chromebook",
            "mini_pc":              "Mini PC / NUC",
        }
    },

    # ── WEEE Cat 4: Display Equipment ─────────────────────────
    "display_equipment": {
        "label":        "🖥️ Display Equipment",
        "weee_cat":     "WEEE Cat 4 — Display Equipment",
        "weee_code":    "WEEE/04",
        "hazard_level": "🚨 High (mercury, lead)",
        "recyclability":"Medium (specialized)",
        "co2_per_kg":   30.0,
        "items": {
            "monitor":              "Computer Monitor (LCD/LED)",
            "television":           "Television Set",
            "led_display":          "LED Display Panel",
            "projector":            "Projector",
            "crt_monitor":          "CRT Monitor (legacy)",
            "digital_photo_frame":  "Digital Photo Frame",
        }
    },

    # ── WEEE Cat 5: Small IT Peripherals ──────────────────────
    "peripherals": {
        "label":        "⌨️ Peripherals & Input Devices",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "🟢 Low",
        "recyclability":"High (plastics, copper)",
        "co2_per_kg":   15.0,
        "items": {
            "keyboard":             "Keyboard",
            "mouse":                "Mouse / Trackpad",
            "trackpad":             "External Trackpad",
            "webcam":               "Webcam",
            "barcode_scanner":      "Barcode Scanner",
            "graphics_tablet":      "Graphics Tablet",
            "joystick":             "Joystick / Game Controller",
            "gamepad":              "Gamepad",
            "numpad":               "Numeric Keypad",
            "card_reader":          "Card Reader",
        }
    },

    # ── WEEE Cat 5: Printing / Scanning Equipment ─────────────
    "printing_scanning": {
        "label":        "🖨️ Printing & Scanning",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "⚠️ Medium (inkjet: chemical)",
        "recyclability":"Medium",
        "co2_per_kg":   20.0,
        "items": {
            "printer":              "Inkjet / Laser Printer",
            "scanner":              "Flatbed Scanner",
            "copier":               "Photocopier / MFP",
            "fax_machine":          "Fax Machine",
            "label_printer":        "Label Printer",
            "3d_printer":           "3D Printer",
        }
    },

    # ── WEEE Cat 3: Networking Equipment ──────────────────────
    "networking_equipment": {
        "label":        "📡 Networking Equipment",
        "weee_cat":     "WEEE Cat 3 — IT & Telecom",
        "weee_code":    "WEEE/03",
        "hazard_level": "🟢 Low",
        "recyclability":"High (metals)",
        "co2_per_kg":   18.0,
        "items": {
            "router":               "Wi-Fi Router",
            "modem":                "DSL / Cable Modem",
            "network_switch":       "Network Switch / Hub",
            "ethernet_hub":         "Ethernet Hub",
            "access_point":         "Wireless Access Point",
            "network_card":         "Network Interface Card",
            "repeater":             "Wi-Fi Repeater / Extender",
        }
    },

    # ── WEEE Cat 5: Computer Components & PCBs ────────────────
    "components_pcb": {
        "label":        "🔧 Components & Circuit Boards",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "🚨 High (PCB: lead, cadmium)",
        "recyclability":"High (precious metals: Au, Ag, Cu, Pd)",
        "co2_per_kg":   35.0,
        "items": {
            "motherboard":          "Motherboard / PCB",
            "circuit_board":        "Generic Circuit Board",
            "gpu":                  "Graphics Card (GPU)",
            "cpu_chip":             "CPU Processor Chip",
            "ram_module":           "RAM Module (DDR/SODIMM)",
            "expansion_card":       "Expansion Card (PCIe/PCI)",
            "sound_card":           "Sound Card",
            "tv_tuner_card":        "TV Tuner Card",
            "capture_card":         "Video Capture Card",
        }
    },

    # ── WEEE Cat 5: Storage Media ──────────────────────────────
    "storage_media": {
        "label":        "💾 Storage Media",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "⚠️ Medium (data security risk)",
        "recyclability":"High (metals, glass platters)",
        "co2_per_kg":   22.0,
        "items": {
            "hard_disk_drive":      "Hard Disk Drive (HDD)",
            "ssd_drive":            "Solid State Drive (SSD)",
            "nvme_drive":           "NVMe M.2 Drive",
            "optical_drive":        "CD/DVD/Blu-ray Drive",
            "floppy_drive":         "Floppy Drive (legacy)",
            "tape_drive":           "Tape Drive",
            "flash_drive":          "USB Flash Drive",
            "memory_card":          "Memory Card (SD/CF)",
            "external_hdd":         "External Hard Drive",
        }
    },

    # ── WEEE Cat 5: Power & Cables ────────────────────────────
    "power_cables": {
        "label":        "🔌 Power Supplies & Cables",
        "weee_cat":     "WEEE Cat 5 — Small IT Equipment",
        "weee_code":    "WEEE/05",
        "hazard_level": "🟢 Low",
        "recyclability":"High (copper, PVC)",
        "co2_per_kg":   12.0,
        "items": {
            "power_supply_unit":    "Power Supply Unit (PSU)",
            "charger":              "Laptop / Device Charger",
            "adapter":              "AC Adapter / Brick",
            "usb_cable":            "USB Cable",
            "hdmi_cable":           "HDMI / DisplayPort Cable",
            "ethernet_cable":       "Ethernet (RJ-45) Cable",
            "power_cable":          "Power / IEC Cable",
            "extension_board":      "Power Extension Strip",
            "cooling_fan":          "Cooling Fan",
            "heat_sink":            "CPU Heat Sink",
            "ups_unit":             "UPS / Battery Backup",
        }
    },

    # ── WEEE Cat 3: Mobile & Portable Devices ─────────────────
    "mobile_devices": {
        "label":        "📱 Mobile & Portable Devices",
        "weee_cat":     "WEEE Cat 3 — IT & Telecom",
        "weee_code":    "WEEE/03",
        "hazard_level": "⚠️ Medium (lithium battery)",
        "recyclability":"High (conflict minerals: Ta, Co)",
        "co2_per_kg":   40.0,
        "items": {
            "smartphone":           "Smartphone",
            "feature_phone":        "Feature Phone (Keypad)",
            "smartwatch":           "Smartwatch / Fitness Band",
            "power_bank":           "Power Bank",
            "walkie_talkie":        "Walkie-Talkie",
            "pager":                "Pager (legacy)",
            "handheld_scanner":     "Handheld Barcode Scanner",
        }
    },

    # ── WEEE Cat 2: Audio/Visual Equipment ────────────────────
    "audio_visual": {
        "label":        "🎵 Audio / Visual Equipment",
        "weee_cat":     "WEEE Cat 2 — AV Equipment",
        "weee_code":    "WEEE/02",
        "hazard_level": "🟢 Low",
        "recyclability":"Medium (mixed materials)",
        "co2_per_kg":   20.0,
        "items": {
            "earbuds":              "Earbuds / In-Ear Monitors",
            "headphones":           "Over-Ear Headphones",
            "bluetooth_speaker":    "Bluetooth Speaker",
            "home_theater":         "Home Theater System",
            "soundbar":             "Soundbar",
            "amplifier":            "Audio Amplifier",
            "dvd_player":           "DVD / Blu-ray Player",
            "media_player":         "Media Streaming Device",
            "camera":               "Digital Camera / DSLR",
            "camcorder":            "Camcorder",
            "remote_control":       "Remote Control",
            "set_top_box":          "Set-Top Box / Cable Box",
        }
    },

    # ── WEEE Cat 1: Home Appliances ─────────────────────────
    "home_appliances": {
        "label":        "🏠 Home Appliances (Electronic)",
        "weee_cat":     "WEEE Cat 1 — Large Household",
        "weee_code":    "WEEE/01",
        "hazard_level": "⚠️ Medium",
        "recyclability":"High (steel, copper)",
        "co2_per_kg":   15.0,
        "items": {
            "microwave":                    "Microwave Oven",
            "electric_kettle":              "Electric Kettle",
            "toaster":                      "Toaster",
            "washing_machine_panel":        "Washing Machine Control Panel",
            "refrigerator_control_board":   "Refrigerator Control Board",
            "electric_fan":                 "Electric Fan",
            "air_purifier":                 "Air Purifier",
            "vacuum_cleaner":               "Vacuum Cleaner",
        }
    },

    # ── WEEE Cat 3: Medical / Scientific Instruments ──────────
    "instruments": {
        "label":        "🔬 Instruments & Tools",
        "weee_cat":     "WEEE Cat 3 — IT Equipment",
        "weee_code":    "WEEE/03",
        "hazard_level": "⚠️ Medium",
        "recyclability":"Medium",
        "co2_per_kg":   20.0,
        "items": {
            "scientific_calculator":    "Scientific Calculator",
            "oscilloscope":             "Oscilloscope",
            "multimeter":               "Digital Multimeter",
            "soldering_iron":           "Soldering Iron",
            "power_meter":              "Power / Energy Meter",
            "gps_device":               "GPS Device",
            "drone":                    "Drone / UAV",
        }
    },
}

# ══════════════════════════════════════════════════════════════════
#  FLAT LOOKUP TABLES  (built automatically from taxonomy)
# ══════════════════════════════════════════════════════════════════
ITEM_SUBCATEGORY:   dict[str, str] = {}   # item_key → subcategory key
ITEM_DISPLAY_NAME:  dict[str, str] = {}   # item_key → human label
ITEM_WEEE_CAT:      dict[str, str] = {}   # item_key → WEEE string
ITEM_WEEE_CODE:     dict[str, str] = {}   # item_key → WEEE/XX code
ITEM_HAZARD:        dict[str, str] = {}   # item_key → hazard level
ITEM_RECYCLABILITY: dict[str, str] = {}   # item_key → recyclability note
ITEM_CO2_PER_KG:    dict[str, float] = {} # item_key → CO2 saving
SUBCATEGORY_LABELS: dict[str, str] = {}   # subcat key → label

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

# All e-waste items (flat list for classification)
EWASTE_ALL: list[str] = list(ITEM_SUBCATEGORY.keys())

# ═══════════════════════════════════════════════════════════════
#  PRIMARY WASTE CATEGORIES
# ═══════════════════════════════════════════════════════════════

# General recyclables + all e-waste items
RECYCLABLE: list[str] = [
    # General recyclables
    "cardboard_box", "can", "plastic_bottle_cap", "plastic_bottle",
    "reuseable_paper", "paper", "cardboard", "aluminum",
    "glass_bottle", "metal_can", "plastic", "newspaper", "magazine",
] + EWASTE_ALL   # all e-waste is also recyclable (specialised)

NON_RECYCLABLE: list[str] = [
    "plastic_bag", "scrap_paper", "stick", "plastic_cup", "snack_bag",
    "plastic_box", "straw", "plastic_cup_lid", "scrap_plastic",
    "cardboard_bowl", "plastic_cultery", "foam", "styrofoam",
    "tissue", "napkin", "food_waste", "organic_waste",
]

HAZARDOUS: list[str] = [
    "chemical_spray_can", "chemical_plastic_bottle",
    "chemical_plastic_gallon", "paint_bucket", "medical_waste",
    "broken_glass", "sharp_objects",
    "battery", "lithium_battery", "light_bulb",
    # E-waste items with hazard override
    "crt_monitor", "motherboard", "circuit_board",
    "gpu", "cpu_chip", "ram_module",
]

# ═══════════════════════════════════════════════════════════════
#  GENERAL YOLO COCO-CLASS → E-WASTE MAPPING
#  (for nano/small/medium models that detect COCO classes)
# ═══════════════════════════════════════════════════════════════
COCO_TO_EWASTE: dict[str, str] = {
    "laptop":       "laptop",
    "cell phone":   "smartphone",
    "tv":           "television",
    "keyboard":     "keyboard",
    "mouse":        "mouse",
    "remote":       "remote_control",
    "microwave":    "microwave",
    "toaster":      "toaster",
    "refrigerator": "refrigerator_control_board",
    "book":         "paper",
    "bottle":       "plastic_bottle",
    "cup":          "plastic_cup",
    "scissors":     "sharp_objects",
    "clock":        "instruments",
    "vase":         "glass_bottle",
}
