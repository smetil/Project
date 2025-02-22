from ultralytics import YOLO
import cv2
import threading
import queue
import time

class EmergencyVehicleDetector:
    def __init__(self, model_path, data_queue, video_source="traffic video.mp4", update_interval=30):
        self.model = YOLO(model_path)
        self.data_queue = data_queue
        self.running = True
        self.video_source = video_source
        self.update_interval = update_interval

    def detect_emergency_vehicles(self):
        cap = cv2.VideoCapture(self.video_source)
        if not cap.isOpened():
            print(f"Error: Could not open video source: {self.video_source}")
            return

        while self.running:
            #if not self.data_queue.empty():
            data = self.data_queue.get()  # Get data from the central server
            sensor_location = data.get("location") #get the location, in case it's useful.
            # Read frame from video
            ret, frame = cap.read()
            if not ret:
                print("End of video or error reading frame. Looping...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
                ret, frame = cap.read()  # Read the first frame
                if not ret:
                    print("Failed to read frame after loop")
                    break

            results = self.model.predict(frame, conf=0.5, verbose=False)
            emergency_detected = False
            directional_counts = {
                "Northbound": 0,
                "Southbound": 0,
                "Eastbound": 0,
                "Westbound": 0,
            }

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0].item())
                    confidence = box.conf[0].item()

                    # Count ALL vehicles
                    if model.names[class_id] in ["car", "truck", "bus", "motorbike"]:
                        direction = self.estimate_direction(box)
                        if direction in directional_counts:
                            directional_counts[direction] += 1

                    if model.names[class_id] == "ambulance" and confidence > 0.7:
                        emergency_detected = True

                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            #Update the frame with Directional data
            cv2.putText(frame, f"North:{directional_counts['Northbound']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"South:{directional_counts['Southbound']}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"East:{directional_counts['Eastbound']}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"West:{directional_counts['Westbound']}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            if emergency_detected:
                cv2.putText(frame, "Emergency Vehicle Detected!", (200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                data["emergency_vehicle_detected"] = True
            else:
                data["emergency_vehicle_detected"] = False #tag it in the frame!


            data["directional_counts"] = directional_counts  # This data is the same for a given frame!
            self.data_queue.put(data)

            cv2.imshow("Emergency Vehicle Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break
            #else:

            #   print("No traffic")

            #No sleep for accurate data!

        cap.release()
        cv2.destroyAllWindows()

    def start(self):
        self.thread = threading.Thread(target=self.detect_emergency_vehicles)
        self.thread.start()

    def stop(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()

    def estimate_direction(self, box):
        frameHeight = 480  # Replace with your video frame height
        frameWidth = 640  # Replace with your video frame width
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        midpointX = (x1 + x2) // 2
        midpointY = (y1 + y2) // 2
        if midpointX < frameWidth // 2:
            return "Westbound"
        else:
            return "Eastbound"  # Return Default

        if midpointY < frameHeight // 2:
            return "Northbound"
        else:
            return "Southbound"

if __name__ == "__main__":
    data_queue = queue.Queue()  # Create queue
    detector = EmergencyVehicleDetector(model_path="best.pt", data_queue=data_queue, video_source="traffic video.mp4")  # Modified Line
    detector.start()
    try:
        while True:
            data = {"location": "Intersection Y"} #pass data to the process.
            #data_queue.put(data) #This stops EVD from getting data, test at your own descrection
            time.sleep(10)  # Add data every 10 seconds
    except KeyboardInterrupt:
        print("Stopping emergency vehicle detection...")
        detector.stop()
