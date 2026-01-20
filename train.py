from ultralytics import YOLO
import onnx

# Load YOLOv11 model (latest version)
model = YOLO('yolov11n.yaml')
model = YOLO('yolov11n.pt')

path = '/content/datasets/waste-detection-9/data.yaml'
results = model.train(data=path, epochs=50, device=0)
results = model.val()
success = model.export(format='onnx')

