#Add a new class
import time
import random
import json
import threading
import queue

class Sensor:
    def __init__(self, location, data_queue):
        self.location = location
        self.data_queue = data_queue
        self.running = True

    def simulate_data(self):
        while self.running:
            data = {
                "timestamp": time.time(),
                "location": self.location,
                "traffic_volume": {
                    "Northbound": random.randint(5, 50),
                    "Southbound": random.randint(10, 60),
                    "Eastbound": random.randint(2, 30),
                    "Westbound": random.randint(7, 45),
                },
                "average_speed": random.randint(20, 60),
                "air_quality": random.uniform(0.0, 1.0),
                "emergency_vehicle_detected": False
            }
            self.data_queue.put(data)  # Put data into the queue
            time.sleep(random.uniform(3, 7))  # Simulate random intervals

    def start(self):
        self.thread = threading.Thread(target=self.simulate_data)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

if __name__ == "__main__":
    data_queue = queue.Queue()  # Create queue
    # Simulate multiple sensors at different locations
    sensor1 = Sensor("Intersection A", data_queue)
    sensor2 = Sensor("Intersection B", data_queue)
    sensor3 = Sensor("Intersection C", data_queue)  # Example
    sensors = [sensor1, sensor2, sensor3]  # add sensors
    # Start each sensor in its own thread
    for sensor in sensors:
        sensor.start()

    try:
        while True:
            if not data_queue.empty():
                data = data_queue.get()  # Get data from the queue
                print(f"Sensor Data Received: {data}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping sensor simulations...")
        for sensor in sensors:
            sensor.stop()
