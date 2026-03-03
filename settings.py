"""
Intelligent Waste Segregation System — Configuration
"""
from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# ─── Paths ────────────────────────────────────────────────
load_dotenv()

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

MODEL_DIR   = ROOT / "weights"
BEST_MODEL  = MODEL_DIR / "best.pt"

# ─── API Keys (loaded from .env) ─────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ─── Camera ───────────────────────────────────────────────
WEBCAM_INDEX = 0

# ─── Waste Categories ────────────────────────────────────
RECYCLABLE = [
    # General
    "cardboard_box", "can", "plastic_bottle_cap", "plastic_bottle",
    "reuseable_paper", "paper", "cardboard", "aluminum",
    "glass_bottle", "metal_can", "plastic", "newspaper", "magazine",
    # E-Waste components
    "laptop", "desktop_cpu", "all_in_one_pc", "monitor", "keyboard",
    "mouse", "trackpad", "printer", "scanner", "router", "modem",
    "motherboard", "circuit_board", "gpu", "cpu_chip", "ram_module",
    "hard_disk_drive", "ssd_drive", "power_supply_unit", "cooling_fan",
    "heat_sink", "expansion_card", "network_card", "charger", "adapter",
    "usb_cable", "hdmi_cable", "ethernet_cable", "power_cable",
    "extension_board", "smartphone", "feature_phone", "tablet",
    "smartwatch", "earbuds", "headphones", "bluetooth_speaker",
    "power_bank", "television", "microwave",
    "refrigerator_control_board", "washing_machine_panel", "ups_unit",
]

NON_RECYCLABLE = [
    "plastic_bag", "scrap_paper", "stick", "plastic_cup", "snack_bag",
    "plastic_box", "straw", "plastic_cup_lid", "scrap_plastic",
    "cardboard_bowl", "plastic_cultery", "foam", "styrofoam",
    "tissue", "napkin", "food_waste", "organic_waste",
]

HAZARDOUS = [
    "chemical_spray_can", "chemical_plastic_bottle",
    "chemical_plastic_gallon", "paint_bucket", "medical_waste",
    "broken_glass", "sharp_objects",
    "battery", "lithium_battery", "light_bulb",
]
