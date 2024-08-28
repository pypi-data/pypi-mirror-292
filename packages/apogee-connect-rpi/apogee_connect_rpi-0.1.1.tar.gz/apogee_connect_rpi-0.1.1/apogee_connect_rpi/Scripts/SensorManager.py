import json
import os

# Class to assist with storing which sensors are currently collecting data
class SensorManager:
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(script_dir)
        self.storage_file = os.path.join(parent_dir, 'json/CollectingSensors.json')

    def _load_sensor_list(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                return data
        else:
            return {}

    def _save_sensor_list(self, sensor_list):
        with open(self.storage_file, 'w') as f:
            json.dump(sensor_list, f, indent=4)

    def add_sensor(self, address: str, interval: int, start_time: int, end_time: int, filename: str, sensorID: int):    
        sensor_list = self._load_sensor_list()
        if address not in sensor_list:
            info = {
                "interval": interval,
                "start_time": start_time,
                "end_time": end_time if end_time is not None else "None", 
                "logs": 0,
                "file": filename,
                "sensorID": sensorID,
                "last_collection_time": start_time # Set to start_time so future start sensors don't attempt data collection until then
            }

            sensor_list[address] = info
            self._save_sensor_list(sensor_list)

    def remove_sensor(self, address):
        sensor_list = self._load_sensor_list()
        if address in sensor_list:
            del sensor_list[address]
            self._save_sensor_list(sensor_list)

    def get_all_sensor_addresses(self):
        sensor_list = self._load_sensor_list()
        return list(sensor_list.keys())
        
    def compile_sensors_for_collection(self, current_time):
        sensor_list = self._load_sensor_list()
        sensor_queue = [
            {
                "address": address,
                "end_time": details['end_time'] if details['end_time'] != "None" else 4294967295, # Make sure end_time isn't None so we can compare against it. 4294967295 = 0xFFFFFFFF
                "file": details['file'],
                "sensorID": details['sensorID'],
                "interval": details['interval']
            }
            for address, details in sensor_list.items()
            if current_time >= (details['last_collection_time'] + (details['interval'] * 60) - 2) # Minus 2 seconds to provide leeway for if script starts slightly quicker than previous time
        ]
        return sensor_queue

    def get_sensor_list_length(self):
        sensor_list = self._load_sensor_list()
        return len(sensor_list)

    def sensor_already_collecting(self, address):
        sensor_list = self._load_sensor_list()
        return address in sensor_list
    
    def increment_collected_logs(self, address):
        sensor_list = self._load_sensor_list()
        if address in sensor_list:
            sensor_list[address]['logs'] += 1
            self._save_sensor_list(sensor_list)
    
    def update_end_time(self, address, end_time):
        sensor_list = self._load_sensor_list()
        if address in sensor_list:
            print("Updating data collection end time")
            sensor_list[address]['end_time'] = end_time
            self._save_sensor_list(sensor_list)
    
    def update_last_collection_time(self, address, time):
        sensor_list = self._load_sensor_list()
        if address in sensor_list:
            print("Updating last data collection time")
            sensor_list[address]['last_collection_time'] = time
            self._save_sensor_list(sensor_list)
    
    def print_collecting_sensor_list(self):
        sensor_list = self._load_sensor_list()
        if not sensor_list:
            print("No sensors are currently collecting data")
        else:    
            print("\n*Currently Collecting Sensors*")
            
            # Print the header row
            headers = ["Address", "Logs", "Interval", "Start Time", "End Time", "File"]
            print("{:^17} | {:^6} | {:^8} | {:^10} | {:^10} | {:^5}".format(*headers))

            # Print the row separator
            print('-' * 18 + '+' + '-' * 8 + '+' + '-' * 10 + '+' + '-' * 12 + '+' + '-' * 12 + '+' + '-' * 6)
            
            # Print the data rows
            for address, details in sensor_list.items():
                print("{:<17} | {:<6} | {:<8} | {:<10} | {:<10} | {:<5}".format(
                    address, 
                    details['logs'], 
                    details['interval'], 
                    details['start_time'], 
                    details['end_time'], 
                    details['file']
                ))