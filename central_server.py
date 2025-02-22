import time
import threading
import queue
from iot_sensors import Sensor
from emergency_vehicle_detection import EmergencyVehicleDetector
from traffic_control import TrafficController
import matplotlib.pyplot as plt

class CentralServer:
    def __init__(self):
        self.sensor_data_queue = queue.Queue()
        self.sensor1 = Sensor("Intersection A", self.sensor_data_queue)
        self.sensor2 = Sensor("Intersection B", self.sensor_data_queue)
        self.sensor3 = Sensor("Intersection C", self.sensor_data_queue)
        self.sensors = [self.sensor1, self.sensor2, self.sensor3]
        self.traffic_controller = TrafficController("Intersection A")
        self.evd = EmergencyVehicleDetector(model_path="best.pt", data_queue=self.sensor_data_queue, video_source="traffic video.mp4")
        self.running = True
        self.emergency_vehicle_count = 0  # Track emergency vehicles
        self.timestamps = [] #Store Graph times
        self.directional_counts_history = [] #Store Graph data
        self.northbound_counts = []  # Store traffic volume and vehicles counts
        self.southbound_counts = []
        self.eastbound_counts = []
        self.westbound_counts = []

    def start(self):
        for sensor in self.sensors:
            sensor.start()
        self.evd.start()
        directional_counts = {"Northbound": 1, "Southbound": 1, "Eastbound": 1, "Westbound": 1}
        self.traffic_controller.start(directional_counts)
        self.server_thread = threading.Thread(target=self.process_sensor_data)
        self.server_thread.start()

    def process_sensor_data(self):
        while self.running:
            try:
                if not self.sensor_data_queue.empty():
                    sensor_data = self.sensor_data_queue.get()
                    location = sensor_data.get('location', 'Unknown Location') # location tag
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # One timestamp

                    print(f"\n{timestamp} - Central Server: Received sensor data from {location}")

                    if "directional_counts" in sensor_data:
                        directional_counts = sensor_data["directional_counts"]
                        print(f"{timestamp} - Directional vehicle counts: {directional_counts}")

                        # Collect historical data
                        self.timestamps.append(timestamp)
                        self.directional_counts_history.append(directional_counts)
                        self.northbound_counts.append(directional_counts["Northbound"])
                        self.southbound_counts.append(directional_counts["Southbound"])
                        self.eastbound_counts.append(directional_counts["Eastbound"])
                        self.westbound_counts.append(directional_counts["Westbound"])

                        self.traffic_controller.adjust_signal_timing(directional_counts)
                        print(f"{timestamp} - Traffic Signal State: {self.traffic_controller.current_state}")
                    # Check for emergency vehicle BEFORE popping to ensure accurate count
                    if "emergency_vehicle_detected" in sensor_data and sensor_data["emergency_vehicle_detected"]:
                        self.emergency_vehicle_count += 1
                        print(f"{timestamp} - Detected Emergency Vehicle. Total count: {self.emergency_vehicle_count}")

                    sensor_data.pop("emergency_vehicle_detected", None)
                    sensor_data.pop("directional_counts", None)
                    #Collect into data

            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error processing sensor data: {e}")
            time.sleep(1)

    def stop(self):
        self.running = False
        for sensor in self.sensors:
            sensor.stop()
        self.evd.stop()
        self.traffic_controller.stop()
        self.server_thread.join()

# Add the graphing function here for correct order of execution
    def display_traffic_graph(self): #Used from data on central server
        #Example data to see data working in central_server
        plt.figure(figsize=(10, 6))
        #This code makes all other functions not work.
        plt.plot(self.timestamps, self.northbound_counts, marker='o', linestyle='-', label='Northbound')
        plt.plot(self.timestamps, self.southbound_counts, marker='o', linestyle='-', label='Southbound')
        plt.plot(self.timestamps, self.eastbound_counts, marker='o', linestyle='-', label='Eastbound')
        plt.plot(self.timestamps, self.westbound_counts, marker='o', linestyle='-', label='Westbound')

        plt.xlabel("Time")
        plt.ylabel("Traffic Volume")
        plt.title("Traffic Volume Over Time")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.legend()

        #If you plot here, all of your functions will stop working!
        plt.show() #This will stop the rest of the code from working because of the pyplot!

if __name__ == "__main__":
    central_server = CentralServer()
    central_server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping the central server...")
        central_server.stop()
        central_server.display_traffic_graph() #Graph!
