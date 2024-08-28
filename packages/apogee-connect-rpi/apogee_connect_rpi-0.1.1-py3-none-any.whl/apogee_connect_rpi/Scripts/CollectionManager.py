import bleak
import struct
import asyncio  
import datetime

from apogee_connect_rpi.Helpers.SensorClasses import *
from apogee_connect_rpi.Helpers.ApogeeUuids import *
from apogee_connect_rpi.Scripts.SensorManager import SensorManager
from apogee_connect_rpi.Scripts.CronManager import CronManager
from apogee_connect_rpi.Scripts.CsvManager import CsvManager
from apogee_connect_rpi.Scripts.ErrorHandling import ErrorHandling


class CollectionManager:
    def __init__(self, address: str, filename: str):
        self.sensorManager = SensorManager()
        self.cronManager = CronManager()
        self.fileManager = CsvManager()

        self.address = address
        self.filename = self.fileManager.get_valid_file(filename, address)
        self.sensor = None
        self.bleak_client = None 

    #
    # SENSOR CONNECTION
    #
    async def connect(self, retries=3, delay=0.5):
        if not self.bleak_client:
            for attempt in range(retries):
                try:
                    print(f"Connecting to sensor {self.address}")
                    self.bleak_client = bleak.BleakClient(self.address)
                    await self.bleak_client.connect()
                    if self.bleak_client.is_connected:
                        ErrorHandling().reset_failure_count()
                        return
                except Exception as e:
                    print(f"Connection attempt {attempt + 1} failed to {self.address}: {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(delay)
                    else:
                        ErrorHandling().increment_failure_count()
                        raise RuntimeError(f"Failed to connect to sensor {self.address}.")

    async def disconnect(self):
        if self.bleak_client:
            try:
                await self.bleak_client.disconnect()
                self.bleak_client = None
            
            except bleak.BleakError as e:
                raise RuntimeError(f"Could not disconnect from sensor {self.address}. {e}")

    #
    # INITIATE COLLECTION
    #
    async def collect_live_data(self, interval: int, start_time, end_time, appending):
        await self.connect()
        await self.populate_sensor_info()
        await self.check_sensor_time()

        if self.sensor is None:
            print("Error retrieving sensor information")
            return
 
        try:           
            self.fileManager.create_csv(self.sensor, self.filename, appending)
 
            await self.set_last_timestamp_transferred(start_time)

            # Configure data logging settings and turn logging on 
            bytearray_data = self.get_logging_bytearray(interval, start_time, end_time)
            await self.initiate_logging(bytearray_data)

            # Add sensor to list of currently collecting sensors
            self.sensorManager.add_sensor(self.sensor.address, interval, start_time, end_time, self.filename, self.sensor.sensorID)

            await self.cronManager.setup_crontab_command_if_needed()         

            print(f"Data collection started. Data will be saved at {self.filename}.\nThis terminal may be closed.")

        except bleak.BleakError as e:
            print(f"Error retrieving sensor data: {e}")
        
        except RuntimeError as e:
            print(e)
        
        finally:
            await self.disconnect()
    
    async def turn_on_gateway_mode(self):
        await self.bleak_client.write_gatt_char(dataLogCollectionRateUUID, bytearray([1]), True)

    async def turn_off_gateway_mode(self):
        await self.bleak_client.write_gatt_char(dataLogCollectionRateUUID, bytearray([0]), True)
                  

    async def set_last_timestamp_transferred(self, time):
        if not time:
            # Set last timestamp transferred to current time to avoid getting unwanted old data
            time = int(datetime.datetime.now().timestamp())

        await self.bleak_client.write_gatt_char(lastTransferredTimestampUUID, bytearray(struct.pack('<I', time)), True)

    def get_logging_bytearray(self, interval: int, start_time, end_time):
        SAMPLING_INTERVAL = 15 # Arbitrarily set to 15 seconds so there's some averaging of data logs
        logging_interval = interval * 60 # Convert to minutes
        data_array = [SAMPLING_INTERVAL, logging_interval]

        # Set start/end time
        data_array.append(start_time)
        if end_time:
            data_array.append(end_time)

        # Convert array to bytearray for gatt characteristic
        bytearray_data = bytearray()
        for num in data_array:
            bytearray_data.extend(struct.pack('<I', num)) 
        
        return bytearray_data

    async def check_sensor_time(self):
        data = await self.bleak_client.read_gatt_char(currentTimeUUID)
        data_packet = bytes(data)
        sensor_time = struct.unpack('<I', data_packet[:4])[0]

        current_time_epoch = int(datetime.datetime.now().timestamp())

        # Update time on sensor if more than a minute off
        time_difference = abs(current_time_epoch - sensor_time)
        if time_difference > 60:
            print("Updating sensor real-time clock")
            await self.bleak_client.write_gatt_char(currentTimeUUID, bytearray(struct.pack('<I', current_time_epoch)), True)      

    async def initiate_logging(self, bytearray_data):
        # Start data logging
        print("Starting data collection...")
        await self.bleak_client.write_gatt_char(dataLoggingIntervalsUUID, bytearray_data, True)
        await self.bleak_client.write_gatt_char(dataLoggingControlUUID, bytearray([1]), True)

    async def populate_sensor_info(self):
        await self.connect()

        try:
            print("Getting sensor info")
            sensorID_data = await self.bleak_client.read_gatt_char(sensorIDUUID)
            hw_data = await self.bleak_client.read_gatt_char(hardwareVersionUUID)
            fw_data = await self.bleak_client.read_gatt_char(firmwareVersionUUID)

            sensorID = int.from_bytes(sensorID_data, byteorder='little', signed=False)           
            hw = int(hw_data.decode('utf-8'))
            fw = int(fw_data.decode('utf-8'))

            self.sensor = get_sensor_class_from_ID(sensorID, self.address)

            if not self.sensor.compatibleFirmware(int(hw), int(fw)):
                raise RuntimeError("Sensor firmware needs to be updated in order to be compatible with this application")
        
        except bleak.BleakError as e:
            raise RuntimeError(f"Error getting sensor info, {e}")

    #
    # DATA COLLECTION
    #
    async def run_data_collection(self, sensorID: int, interval: int, end_time: int, current_time_epoch: int):
        await self.connect()
        self.sensor = get_sensor_class_from_ID(sensorID, self.address)

        try:
            keep_collecting = True
            iter = 0 # Fail-safe to avoid infinite loop
            while keep_collecting and iter < 100:
                data = await self.bleak_client.read_gatt_char(dataLogTransferUUID)
                keep_collecting = await self.process_data_packet(data, end_time)

            # Go one extra interval past end_time just in case log was ready in time for last collect
            if current_time_epoch > (end_time + interval * 60):
                print("Current time after end time; stopping data collection")
                await self.stop_data_collection()

            self.sensorManager.update_last_collection_time(self.address, current_time_epoch)

        except Exception as e:
            print(f"Sensor error: {self.address}. {e}")

        finally:
            await self.disconnect()

    async def process_data_packet(self, data, end_time: int): 
        data_packet = bytes(data)
        hex_representation = data_packet.hex()
        print(f"Received data packet: {hex_representation}")

        # Check if data packet is incomplete or if it is just all "FF" indicating end of data
        if len(data_packet) < 8 or hex_representation == 'ffffffff':
            print("No more data to collect")
            return False
              
        # Get packet header information
        timestamp = struct.unpack('<I', data_packet[:4])[0]
        intervalBetweenTimestamps = struct.unpack('<H', data_packet[4:6])[0]
        measurementsPerInterval = struct.unpack('<B', data_packet[6:7])[0]
                
        data = []
        # This loop should usually only run once, but just in case a collection is missed and there are multiple sets in packet
        # Separate packet into groups based on timestamp (e.g., groups of 5 datapoints for the Guardian, groups of 1 datapoint for microcache)
        for startIndex in range(8, len(data_packet) - 1, 4 * measurementsPerInterval):
            if timestamp > end_time:
                print("Current collect timestamp after end time; stopping data collection")
                await self.stop_data_collection()
                return False

            endIndex = min(startIndex + (4 * measurementsPerInterval), len(data_packet))
            groupedArray = data_packet[startIndex:endIndex]

            # Get each datapoint within the current timestamp
            data = []
            for i in range(0, len(groupedArray), 4):
                raw = struct.unpack('<i', groupedArray[i:(i + 4)])[0]

                # Divide by 10,000 to scale from ten-thousandths to ones
                dataValue = raw / 10000.0

                data.append(dataValue)

            # Calculate all live data based on specific sensor class
            live_data = self.sensor.calculate_live_data(data)

            self.fileManager.write_to_csv(timestamp, live_data, self.sensor, self.filename)
            self.sensorManager.increment_collected_logs(self.address)

            # Increment timestamp in case there are multiple logs in a single packet
            timestamp += intervalBetweenTimestamps

        return True

    # 
    # STOP COLLECTION
    #
    async def stop_data_collection(self):
        await self.connect()
            
        print("Stopping Live Data")
        await self.bleak_client.write_gatt_char(dataLoggingControlUUID, bytearray([0]), True)

        print("Removing sensor from list")
        self.sensorManager.remove_sensor(self.address)

        if self.sensorManager.get_sensor_list_length() <= 0:
            self.cronManager.remove_crontab_job()

        await self.disconnect()