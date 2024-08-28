import datetime

from apogee_connect_rpi.Scripts.BleScanner import BleScanner
from apogee_connect_rpi.Scripts.SensorManager import SensorManager
from apogee_connect_rpi.Scripts.CollectionManager import CollectionManager
from apogee_connect_rpi.Scripts.AppConfig import AppConfig

class CommandImplement:
    def __init__(self):
        self.sensorManager = SensorManager()

    # 
    # COLLECT
    #
    async def collect(self, args):
        address = args.address

        if self.sensorManager.sensor_already_collecting(address):
            raise RuntimeError("Sensor is already collecting data")
        
        if self.max_sensors_reached():
            raise RuntimeError("\nMaximum of 5 sensors currently collecting data. Use 'list' command to see currently collecting sensors.")
        
        start, end = self.get_start_end_time(args)

        collectionManager = CollectionManager(address, args.file)
        await collectionManager.collect_live_data(args.interval, start, end, args.append)
    
    def max_sensors_reached(self) -> bool:
        MAX_SENSORS = 5
        current_sensor_length = self.sensorManager.get_sensor_list_length()
        return current_sensor_length >= MAX_SENSORS
    
    def get_start_end_time(self, args):
        current_time_epoch = int(datetime.datetime.now().timestamp())
        start = args.start
        end = args.end
        if not start:
            start = current_time_epoch
        if end:
            if (end <= start) or (end <= current_time_epoch):
                raise ValueError("End time must be after the start time and the current time")
            
        return start, end        

    # 
    # CONFIG
    #
    async def config(self, args):
        config = AppConfig()

        # Just print the config if no arguments included with command
        if all(arg is None for arg in vars(args).values()):
            config.print_config()
        else:
            config.update_config(args)

    #
    # LIST
    #
    async def list(self):
        self.sensorManager.print_collecting_sensor_list()

    #
    # SCAN
    #
    async def scan(self, args):
        scan_time = args.time
        run_until_no_missing_packets = False

        # If no scan time was set, run at least 5 seconds until no discovered sensors are missing packets
        if not scan_time:
            scan_time = 5
            run_until_no_missing_packets = True

        scanner = BleScanner(scan_time, run_until_no_missing_packets)
        await scanner.startScan()

    #
    # STOP
    #
    async def stop(self, args):
        address = args.address
        end_time = args.end 

        if end_time:
            self.sensorManager.update_end_time(address, end_time)
        else:
            collectionManager = CollectionManager(address, "")
            await collectionManager.stop_data_collection()
    
    async def stop_all(self):
        sensor_addresses = self.sensorManager.get_all_sensor_addresses()
        for address in sensor_addresses:
            try:
                collectionManager = CollectionManager(address, "")
                await collectionManager.stop_data_collection()
            except Exception as e:
                print(e)


    #
    # CRONTAB DATA COLLECTION
    #
    async def run_data_collection(self):
        current_time = datetime.datetime.now()
        current_time_epoch = int(current_time.timestamp())
        sensors_queue = self.sensorManager.compile_sensors_for_collection(current_time_epoch)

        print(f"\n{current_time}")
        print(f"Collecting from: {', '.join(sensor['address'] for sensor in sensors_queue)}")

        for sensor in sensors_queue:
            try:
                address = sensor['address']
                file = sensor['file']
                sensorID = sensor['sensorID']
                interval = sensor['interval']
                end_time = sensor['end_time']

                collectionManager = CollectionManager(address, file)
                await collectionManager.run_data_collection(sensorID, interval, end_time, current_time_epoch)
            except Exception as e:
                print(e)
        
        print(f"Exiting scheduled data collection at {datetime.datetime.now()}")