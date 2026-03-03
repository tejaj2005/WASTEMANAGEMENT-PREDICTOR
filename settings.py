from pathlib import Path
import sys

file_path = Path(__file__).resolve()
root_path = file_path.parent
if root_path not in sys.path:
    sys.path.append(str(root_path))

ROOT = root_path

# Model paths
MODEL_DIR = ROOT / "weights"
DETECTION_MODEL = MODEL_DIR / "best.pt"

# Google Gemini API Key
GEMINI_API_KEY = "AIzaSyBj_-jxwNdsmHoXtvBriSH6sgioiPqiyww"

# Webcam (0 = laptop webcam)
WEBCAM_PATH = 0

# Waste categories - Extended for better detection
RECYCLABLE = [
    # General Recyclables
    "cardboard_box", "can", "plastic_bottle_cap", "plastic_bottle",
    "reuseable_paper", "paper", "cardboard", "aluminum",
    "glass_bottle", "metal_can", "plastic", "newspaper", "magazine",
    
    # E-Waste (Recyclable components)
    "laptop", "desktop_cpu", "all_in_one_pc", "monitor", "keyboard", "mouse",
    "trackpad", "printer", "scanner", "router", "modem", "motherboard",
    "circuit_board", "gpu", "cpu_chip", "ram_module", "hard_disk_drive",
    "ssd_drive", "power_supply_unit", "cooling_fan", "heat_sink",
    "expansion_card", "network_card", "charger", "adapter", "usb_cable",
    "hdmi_cable", "ethernet_cable", "power_cable", "extension_board",
    "smartphone", "feature_phone", "tablet", "smartwatch", "earbuds",
    "headphones", "bluetooth_speaker", "power_bank",
    "television", "microwave", "refrigerator_control_board", "washing_machine_panel",
    "ups_unit"
]

NON_RECYCLABLE = [
    "plastic_bag", "scrap_paper", "stick", "plastic_cup", "snack_bag",
    "plastic_box", "straw", "plastic_cup_lid", "scrap_plastic",
    "cardboard_bowl", "plastic_cultery", "foam", "styrofoam",
    "tissue", "napkin", "food_waste", "organic_waste"
]

HAZARDOUS = [
    # General Hazardous
    "chemical_spray_can", "chemical_plastic_bottle", "chemical_plastic_gallon",
    "paint_bucket", "medical_waste", "broken_glass", "sharp_objects",
    
    # E-Waste Hazards
    "battery", "lithium_battery", "light_bulb"
]
