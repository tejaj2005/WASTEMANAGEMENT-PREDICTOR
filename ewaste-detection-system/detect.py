import os
import cv2
import json
import torch
from ultralytics import YOLO
from intelligence_layer import EWasteIntelligence
import argparse
import time

def process_source(source, model_path='yolov8x_custom_ewaste/weights/best.pt', conf_thresh=0.6, iou_thresh=0.7):
    # Check if model exists, if not use base model for demo (though classes won't match perfectly)
    if not os.path.exists(model_path):
        print(f"Warning: Custom trained model not found at {model_path}. Using base yolov8x.pt (classes will be incorrect).")
        model_path = 'yolov8x.pt'

    print(f"Loading model: {model_path}")
    model = YOLO(model_path)
    intelligence = EWasteIntelligence()

    # Inference options
    # User requested: IoU 0.7+, Conf 0.6+
    results = model(source, stream=True, conf=conf_thresh, iou=iou_thresh)

    for r in results:
        boxes = r.boxes
        img = r.orig_img.copy()

        detected_objects = []

        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Get class name from model names
            if model.names and cls_id in model.names:
                class_name = model.names[cls_id]
            else:
                class_name = f"Class_{cls_id}"

            # Get Intelligence Data
            analysis = intelligence.analyze(class_name, conf)
            detected_objects.append(analysis)

            # Draw Bounding Box & Label
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = (0, 255, 0) # Green
            if analysis.get('safety_alert', {}).get('is_hazardous'):
                color = (0, 0, 255) # Red for hazardous

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            label = f"{class_name} {conf:.2f}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Print Analysis to Console
            print(json.dumps(analysis, indent=2))

        # Show Image
        cv2.imshow('E-Waste Detection System', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, default='0', help='Path to image/video or 0 for webcam')
    parser.add_argument('--weights', type=str, default='ewaste_project/yolov8x_custom_ewaste/weights/best.pt', help='Path to trained weights')
    args = parser.parse_args()
    
    process_source(args.source, args.weights)
