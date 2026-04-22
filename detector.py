from ultralytics import YOLO
import numpy as np
import cv2

class ObjectDetector:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)

    def detect(self, frame):
        frame = cv2.resize(frame, (640, 480))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.model.predict(frame_rgb, conf=0.3, verbose=False)[0]

        detections = []

        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])

                detections.append([x1, y1, x2, y2, conf, cls])

        return np.array(detections) if detections else np.empty((0, 6))

    def get_class_name(self, class_id):
        return self.model.names[class_id]