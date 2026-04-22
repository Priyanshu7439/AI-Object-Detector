import cv2
import numpy as np

def get_colors(num_colors):
    """
    Generate a set of distinct colors for drawing.
    """
    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(num_colors, 3), dtype=np.uint8)
    return [tuple(map(int, c)) for c in colors]

# Pre-generate some colors
box_colors = get_colors(100)

def draw_detections(frame, tracked_objects, detector):
    """
    Draw bounding boxes and labels on the frame.
    :param frame: The frame to draw on.
    :param tracked_objects: List of tracking results [[x1, y1, x2, y2, id], ...]
    :param detector: The detector object to get class names.
    :return: Annotated frame.
    """
    for obj in tracked_objects:
        x1, y1, x2, y2, obj_id = map(int, obj)
        
        color = box_colors[obj_id % len(box_colors)]
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Create label
        label = f"ID: {obj_id}"
        
        # Put label text
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
    return frame

def preprocess_frame(frame, width=640, height=480):
    """
    Resize the frame for better performance.
    """
    return cv2.resize(frame, (width, height))
