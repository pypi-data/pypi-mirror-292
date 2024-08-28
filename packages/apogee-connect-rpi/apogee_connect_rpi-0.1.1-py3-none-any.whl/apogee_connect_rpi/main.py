#!/usr/bin/env python3

import asyncio
import argparse
import sys
import re
import datetime
from filelock import FileLock, Timeout
from textwrap import dedent
from apogee_connect_rpi.Scripts.CommandImplement import CommandImplement
from apogee_connect_rpi.version import __version__

class Main:
    def __init__(self):
        self.commandImplement = CommandImplement()

        # Map command name to function name
        self.COMMAND_MAP = {
            'collect': 'collect',
            'config': 'config',
            'list': 'list',
            'scan': 'scan',
            'stop': 'stop',
            'run-data-collection': 'run_data_collection'
        }

        self.parser = argparse.ArgumentParser(
            description='Apogee Connect for Raspberry Pi',
            usage=dedent('''
                Interact with Apogee bluetooth sensors for automatic data collection
                         
                Available Commands:
                collect    Collect data from a sensor
                config     Change or read app configuration
                list       Show a list of currently collecting sensors
                scan       Scan for nearby sensors
                stop       Stop data collection for a sensor
            '''))
        
        self.parser.add_argument('command', help='Any command from the above list may be used')
        self.parser.add_argument('-v', '--version', action='version', version=__version__, help='Show version number of application')

        try:
            args = self.parser.parse_args(sys.argv[1:2])

            asyncio.run(self.dispatch_command(args.command))
        except Exception as e:
            print(e)

    async def dispatch_command(self, command):
        func_name = self.COMMAND_MAP.get(command)
    
        if func_name and hasattr(self, func_name):
            method = getattr(self, func_name)
            await method()
        else:
            self.parser.print_help()
            raise ValueError('\nUnrecognized command. See the above help menu')

    #
    # COMMANDS
    #   
    async def collect(self):
        parser = argparse.ArgumentParser(description='Collect data from an Apogee sensor via bluetooth')
        parser.add_argument('address', type=self._mac_address,
                            help='MAC address of sensor in the format of XX:XX:XX:XX:XX:XX')
        parser.add_argument('-i', '--interval', metavar='INTERVAL', type=self._positive_int, default=5,
                            help="Collect data every INTERVAL minutes (must be a positive integer)")
        parser.add_argument('-s', '--start', metavar='START', type=self._positive_int,
                            help="Start time for data collection using epoch time (Unix timestamp in seconds)")
        parser.add_argument('-e', '--end', metavar='END', type=self._positive_int,
                            help="End time for data collection using epoch time (Unix timestamp in seconds)")
        parser.add_argument('-f', '--file', metavar='FILE', type=str,
                            help="Filepath to write data to csv file")
        parser.add_argument('-a', '--append', action='store_true',
                            help="Append to file instead of overwriting")
        args = parser.parse_args(sys.argv[2:])

        await self.commandImplement.collect(args)
        
    async def config(self):
        parser = argparse.ArgumentParser(description='Collect data from an Apogee sensor via bluetooth at desired intervals')
        parser.add_argument('-p', '--precision', metavar='PRECISION', type=self._positive_int,
                            help="Change the maximum number of decimals displayed for data")
        parser.add_argument('-f', '--filepath', metavar='FILEPATH', type=str,
                            help="The default folder to save collected data.")
        parser.add_argument('-t', '--temp', metavar='TEMP', type=self._valid_temp,
                            help="Change preferred temperature units. Enter “C” for Celsius and “F” for Fahrenheit (without quotations).")
        parser.add_argument('-pf', '--par-filtering', metavar='PAR_FILTERING', type=self._adaptable_bool,
                            help='Filter negative PAR (PPFD) values to compensate for sensor "noise" in low-light conditions. Enter "True" or "False" (without quotations)')

        args = parser.parse_args(sys.argv[2:])

        await self.commandImplement.config(args)

    async def list(self):
        parser = argparse.ArgumentParser(description='Show list of Apogee bluetooth sensors that are currently collecting data')
        args = parser.parse_args(sys.argv[2:])

        await self.commandImplement.list()

    async def scan(self):
        parser = argparse.ArgumentParser(description='Scan for nearby Apogee bluetooth sensors')
        parser.add_argument('-t', '--time', metavar='TIME', type=self._positive_int,
                            help="Scan for TIME seconds")
        args = parser.parse_args(sys.argv[2:])

        await self.commandImplement.scan(args)

    async def stop(self):
        parser = argparse.ArgumentParser(description='Stop data collection from an Apogee sensor via bluetooth')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('address', type=self._mac_address, nargs='?',
                           help='MAC address of sensor in the format of XX:XX:XX:XX:XX:XX')
        group.add_argument('-a', '--all', action='store_true',
                           help='Stop data collection from all sensors')
        parser.add_argument('-e', '--end', metavar='END', type=self._positive_int,
                            help="End time for data collection using epoch time (Unix timestamp in seconds)")
        args = parser.parse_args(sys.argv[2:])

        if args.all and args.end is not None:
            raise ValueError("End time cannot be set when using '--all'")

        if args.all:
            await self.commandImplement.stop_all()
        else:
            await self.commandImplement.stop(args)        

    # This function is only intended to be run by crontab command on a schedule, never by a user, thus the longer command name
    async def run_data_collection(self):
        parser = argparse.ArgumentParser(description='Private command run by crontab scheduler')        
        args = parser.parse_args(sys.argv[2:])

        try:
            # Avoid duplicate data collection processes from running
            with FileLock("/tmp/apogee_connect_rpi.lock").acquire(timeout=10):
                await self.commandImplement.run_data_collection()
        except Timeout as e:
            print(f"\n{e}")
            print(f"The previous data collection process is still running. Skipping this instance.")
        except Exception as e:
            print(f"\n{e}")
            

    #
    # CUSTOM DATA TYPES
    #   
    def _positive_int(self, value):
        try:
            value_int = int(value)
            if value_int <= 0:
                raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
            return value_int
        except ValueError:
            raise argparse.ArgumentTypeError(f"{value} is not a valid integer")

    def _mac_address(self, value):
        pattern = re.compile("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
        if not pattern.match(value):
            raise argparse.ArgumentTypeError(f"{value} is not a valid MAC address. Format must follow XX:XX:XX:XX:XX:XX")
        return value
    
    def _valid_temp(self, value):
        if value.upper() not in ['C', 'F']:
            raise argparse.ArgumentTypeError(f"Invalid temperature unit '{value}'. Must be 'C' or 'F'.")
        return value.upper()
    
    def _adaptable_bool(self, value):
        if value.lower() in ('true', '1', 't'):
            return True
        elif value.lower() in ('false', '0', 'f'):
            return False
        else:
            raise argparse.ArgumentTypeError(f"Boolean value expected (true/false), got '{value}'.")

#
# MAIN
#  
def main():
    Main()

if __name__ == '__main__':
    main()