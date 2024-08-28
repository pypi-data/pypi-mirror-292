import os
import csv
import datetime

from apogee_connect_rpi.Helpers.liveDataTypes import liveDataTypes
from apogee_connect_rpi.Scripts.AppConfig import AppConfig

class CsvManager:
    def __init__(self):
        self.config = AppConfig()
    
    def write_to_csv(self, timestamp, live_data, sensor, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        file_exists = os.path.isfile(filename)

        if not file_exists:
            self.create_csv(sensor, filename)

        precision = self.get_precision()

        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')

            datetime = self.convert_timestamp_dattime(timestamp)
            truncated_values = [datetime] + [self.truncate_float(value, precision) for value in live_data]
            writer.writerow(truncated_values)
    
    def create_csv(self, sensor, filename, appending = False):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        file_exists = os.path.isfile(filename)

        if file_exists and appending:
            print("Appending data to existing file")
            return
        
        if file_exists and not appending:
            overwrite = input(f"\nThe file '{filename}' already exists. If you want to append to the existing file, use the flag '-a' with your collect command.\nDo you want to overwrite it? [Y/N]: ")
            if overwrite.lower() != 'y':
                raise RuntimeError("File not overwritten. Exiting command.")
            else:
                print("Overwriting file")
            
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            labels_with_units = ["Timestamp"] + [self.format_label_with_units(label) for label in sensor.live_data_labels]
            writer.writerow(labels_with_units)
   
    def get_valid_file(self, file, address):
        # If file is provided, it must be a csv file
        if file and not file.endswith('.csv'):
            raise ValueError("The 'file' parameter must have a '.csv' extension")
        
        # Default case
        if not file:
            path = AppConfig().get_default_filepath()
            return os.path.join(path, "{}.csv".format(address.replace(':', '-')))
        
        # Just a file name and no filepath
        if not os.path.dirname(file):
            path = AppConfig().get_default_filepath()
            return os.path.join(path, f"{file}")
        
        file = os.path.normpath(file)
        # Check for relative filepath vs absolute filepath
        if os.path.isabs(file):
            return file
        else:
            return os.path.join(os.getcwd(), file)

    #
    # HELPERS
    #     
    def format_label_with_units(self, label):
        if label in liveDataTypes:
            units = liveDataTypes[label]["units"]
            return f"{label} ({units})"
        else:
            return label
    
    def truncate_float(self, value, precision=2):
        return f"{value:.{precision}f}"
    
    def convert_timestamp_dattime(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%c')
    
    def get_precision(self):
        return self.config.get_precision()