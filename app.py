import cv2
from flask import Flask, render_template, Response, jsonify
from detector import ObjectDetector
from tracker import Sort
import numpy as np

app = Flask(__name__)

video_capture = None
is_running = False

detector = ObjectDetector()
tracker = Sort(max_age=10, min_hits=1, iou_threshold=0.3)

# Store labels for stable tracking
id_to_label = {}


def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return interArea / float(boxAArea + boxBArea - interArea + 1e-6)


def generate_frames():
    global video_capture, is_running, id_to_label

    while is_running:
        success, frame = video_capture.read()
        if not success:
            break

        frame = cv2.resize(frame, (640, 480))

        #DETECTION
        detections = detector.detect(frame)

        #TRACKING
        if len(detections) > 0:
            dets_for_tracker = detections[:, :5]
            tracked_objects = tracker.update(dets_for_tracker)
        else:
            tracked_objects = np.empty((0, 5))

        #DRAW (Label + ID ALWAYS shown)
        
        for obj in tracked_objects:
            x1, y1, x2, y2, obj_id = obj
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            obj_id = int(obj_id)

            best_label = None
            best_iou = 0.0
            max_distance_threshold = 80  # pixels

            # center of tracked box
            cx_obj = (x1 + x2) / 2.0
            cy_obj = (y1 + y2) / 2.0

            # try to match with detections using IOU + distance
            for det in detections:
                dx1, dy1, dx2, dy2, conf, cls = det
                dx1, dy1, dx2, dy2 = int(dx1), int(dy1), int(dx2), int(dy2)

                # calculate IOU
                iou = compute_iou([x1, y1, x2, y2], [dx1, dy1, dx2, dy2])

                # calculate center distance
                cx_det = (dx1 + dx2) / 2.0
                cy_det = (dy1 + dy2) / 2.0
                distance = ((cx_obj - cx_det) ** 2 + (cy_obj - cy_det) ** 2) ** 0.5

                # match if IOU > 0.1 OR distance is small
                if (iou > 0.1 or distance < max_distance_threshold):
                    # prioritize by highest IOU, then by distance
                    if iou > best_iou:
                        best_iou = iou
                        best_label = detector.get_class_name(int(cls))

            # store label only if matched
            if best_label and best_iou > 0:
                id_to_label[obj_id] = best_label

            # always display label + ID (use persisted label if current detection fails)
            label_name = id_to_label.get(obj_id, "Unknown Object")
            label = f"{label_name} | ID {obj_id}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    if video_capture:
        video_capture.release()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    if not is_running:
        return "Video feed not started", 404

    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/start_feed')
def start_feed():
    global video_capture, is_running

    if not is_running:
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            return jsonify({"status": "error", "message": "Webcam not working"}), 500

        is_running = True
        return jsonify({"status": "started"})

    return jsonify({"status": "already running"})


@app.route('/stop_feed')
def stop_feed():
    global is_running
    is_running = False
    return jsonify({"status": "stopped"})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
