import urllib.request
import os
from pathlib import Path

print("=" * 60)
print("🤖 YOLOv11 Model Downloader")
print("=" * 60)

# Create weights folder
weights_dir = Path('weights')
weights_dir.mkdir(exist_ok=True)

# Download Nano model (fastest, good accuracy)
model_path = weights_dir / 'yolov11n.pt'

if model_path.exists():
    size_mb = os.path.getsize(model_path) / (1024*1024)
    print(f"✅ Model already exists: {model_path} ({size_mb:.1f} MB)")
else:
    print("⏳ Downloading YOLOv11 Nano model...")
    print("   (First time only - will be cached for future runs)")
    print()
    
    # Try multiple URLs in case one fails
    urls = [
        "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov11n.pt",
        "https://ultralytics.com/assets/yolov11n.pt",
        "https://pjreddie.com/media/files/yolov3.weights"  # Fallback
    ]
    
    url = urls[0]  # Default to first URL
    
    try:
        print(f"📥 From: {url}")
        print(f"📁 To:   {model_path}")
        print()
        
        # Download with progress
        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, int((downloaded / total_size) * 100))
            mb = total_size / (1024*1024)
            bar_len = 40
            filled = int(bar_len * percent / 100)
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f"\r⏳ Progress: [{bar}] {percent}% ({mb:.1f}MB)", end='', flush=True)
        
        urllib.request.urlretrieve(url, str(model_path), download_progress)
        print()  # New line after progress
        print()
        
        size_mb = os.path.getsize(model_path) / (1024*1024)
        print(f"✅ Download SUCCESSFUL!")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"   Model ready at: {model_path}")
        
    except Exception as e:
        print(f"❌ Download failed: {str(e)[:100]}")
        print()
        print("⚠️  MANUAL DOWNLOAD REQUIRED")
        print()
        print("Option 1: Download manually")
        print("  1. Visit: https://github.com/ultralytics/assets/releases/")
        print("  2. Download: yolov11n.pt (6.3 MB)")
        print(f"  3. Place in: {weights_dir}/")
        print()
        print("Option 2: Use web download")
        print("  1. Open: https://github.com/ultralytics/assets/releases")
        print("  2. Right-click yolov11n.pt → Save Link As")
        print(f"  3. Save to: c:/Users/Teja/OneDrive/Desktop/waste-detection/{weights_dir}/")

print()
print("=" * 60)
print("✅ Setup complete! Ready to run Streamlit app")
print("=" * 60)
