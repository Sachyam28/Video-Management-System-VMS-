from ultralytics import YOLO
import cv2
import numpy as np


# ----------------------------------------
# YOLOv8 ROAD OBJECT DETECTION MODEL
# ----------------------------------------
class RoadDetectorModel:
    def __init__(self):
        print("[Model] Loading YOLOv8n general model...")
        self.model = YOLO("yolov8n.pt")

    def predict(self, frame):
        results = self.model.predict(frame, conf=0.25, verbose=False)

        detections = []
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = r.names[cls]
                score = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                detections.append({
                    "label": label,
                    "score": score,
                    "bbox": [x1, y1, x2, y2]
                })

        return {"detections": detections}


# ----------------------------------------
# CRACK & POTHOLE DETECTOR (NO DOWNLOAD NEEDED)
# ----------------------------------------
class CrackPotholeDetectorModel:
    def __init__(self):
        print("[Model] Using classical + YOLO hybrid crack detector")

    def predict(self, frame):
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Edge detection (crack-like patterns)
        edges = cv2.Canny(gray, 50, 150)

        # Count edge pixels
        crack_score = float(np.sum(edges > 0) / edges.size)

        # Heuristic threshold for cracks/potholes
        alert = crack_score > 0.02  # ~2% pixels are sharp edges

        detections = []
        if alert:
            detections.append({
                "label": "crack_or_pothole",
                "score": crack_score,
                "bbox": [0, 0, frame.shape[1], frame.shape[0]]
            })

        return {
            "detections": detections,
            "crack_score": crack_score,
            "alert": alert
        }


# ----------------------------------------
# MODEL REGISTRY
# ----------------------------------------
MODEL_REGISTRY = {
    "road_detector": RoadDetectorModel,
    "crack_detector": CrackPotholeDetectorModel,
}
