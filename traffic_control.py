import time
import random

class TrafficController:
    def __init__(self, intersection):
        self.intersection = intersection
        self.current_state = "Green"  # Initial state
        self.green_duration = 30
        self.yellow_duration = 5
        self.red_duration = 30
        self.running = True

    def adjust_signal_timing(self, directional_counts):
        total_volume = sum(directional_counts.values())
        if total_volume == 0:
            print("No traffic")
            return

        green_times = {}
        for direction, volume in directional_counts.items():
            green_times[direction] = self.calculate_green_time(volume, total_volume)
        print(f"New Green Light Durations for {self.intersection}: {green_times}")

        # Implement the signal change logic HERE (simplified for now)
        #  Example:  Set self.green_duration based on the highest green_time
        max_green_time = max(green_times.values())
        self.green_duration = max_green_time


    def calculate_green_time(self, volume, total_volume):
        base_green_time = 10  # Minimum green time
        max_green_time = 60  # Maximum green time
        ratio = volume / total_volume
        green_time = base_green_time + (max_green_time - base_green_time) * ratio
        return max(base_green_time, min(max_green_time, green_time))

    def run_cycle(self, directional_counts): #Modified run Cycle
        while self.running:

            # Adjust signal timing based on traffic volume
            #Added check to see if there was a result from EVD or the program would crash!

            if directional_counts:
                 self.adjust_signal_timing(directional_counts)
            else:
                print("There was no EVD result for 1 traffic cycle, defaulting Green")
                #We set it to 1 if there was nothing.
                self.adjust_signal_timing({"Northbound": 1, "Southbound": 1, "Eastbound": 1, "Westbound":1})

            print(f"{self.intersection}: {self.current_state}")

            if self.current_state == "Green":
                time.sleep(self.green_duration)
                self.current_state = "Yellow"

            elif self.current_state == "Yellow":
                time.sleep(self.yellow_duration)
                self.current_state = "Red"

            elif self.current_state == "Red":
                time.sleep(self.red_duration)
                self.current_state = "Green"

    def override_signal(self, duration=15):
        print(f"Override: Setting {self.intersection} to Green for {duration} seconds!")
        self.current_state = "Green"
        time.sleep(duration)
        print("Override complete. Resuming normal traffic signal cycle.")

    def start(self,directional_counts):
        self.thread = threading.Thread(target=self.run_cycle,args=(directional_counts,))
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

if __name__ == "__main__":
    traffic_controller = TrafficController("Intersection A")
    #Needs directional counts, can no longer start it here with the threads going!
    traffic_controller.start({"Northbound": 1, "Southbound": 1, "Eastbound": 1, "Westbound":1})

    time.sleep(5) #Let simulation Run for 5 seconds
    traffic_controller.override_signal()
    traffic_controller.stop()
