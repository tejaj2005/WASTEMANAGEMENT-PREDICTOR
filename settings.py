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

# Webcam (0 = laptop webcam)
WEBCAM_PATH = 0

# Waste categories - Extended for better detection
RECYCLABLE = [
    "cardboard_box",
    "can",
    "plastic_bottle_cap",
    "plastic_bottle",
    "reuseable_paper",
    "paper",
    "cardboard",
    "aluminum",
    "glass_bottle",
    "metal_can",
    "plastic",
    "newspaper",
    "magazine"
]

NON_RECYCLABLE = [
    "plastic_bag",
    "scrap_paper",
    "stick",
    "plastic_cup",
    "snack_bag",
    "plastic_box",
    "straw",
    "plastic_cup_lid",
    "scrap_plastic",
    "cardboard_bowl",
    "plastic_cultery",
    "foam",
    "styrofoam",
    "tissue",
    "napkin",
    "food_waste",
    "organic_waste"
]

HAZARDOUS = [
    "battery",
    "chemical_spray_can",
    "chemical_plastic_bottle",
    "chemical_plastic_gallon",
    "light_bulb",
    "paint_bucket",
    "electronic_waste",
    "broken_glass",
    "sharp_objects",
    "medical_waste"
]
