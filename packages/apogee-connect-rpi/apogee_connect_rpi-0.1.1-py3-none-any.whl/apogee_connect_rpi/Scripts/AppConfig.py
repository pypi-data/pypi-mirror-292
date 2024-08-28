import json
import os

class AppConfig:    
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(script_dir)
        self.config_file = os.path.join(parent_dir, 'json/AppConfig.json')

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
            
        except FileNotFoundError:
            print(f"Config file '{self.config_file}' not found. Using default settings.")
            return{}

    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
            print("Config updated")

    def print_config(self):
        config = self.load_config()
        print(json.dumps(config, indent=4))

    def update_config(self, args):
        config = self.load_config()

        if args.precision is not None:
            self.set_precision(config, args.precision)
        
        if args.temp is not None:
            self.set_temp_units(config, args.temp)

        if args.par_filtering is not None:
            self.set_par_filtering(config, args.par_filtering)

        if args.filepath is not None:
            self.set_default_filepath(config, args.filepath)
        
        self.save_config(config)
            
    #
    # PRECISION
    #
    def get_precision(self):
        config = self.load_config()
        return config.get('precision', 2)

    def set_precision(self, config, precision: int):
        print("Updating precision")
        config['precision'] = precision

    #
    # UNITS
    #
    def get_temp_units(self):
        config = self.load_config()
        return config.get('units', {}).get('temperature')

    def set_temp_units(self, config, unit):
        print("Updating temperature units")
        if unit not in ["C", "F"]:
            raise ValueError("Unit must be 'C' (Celsius) or 'F' (Fahrenheit)")

        if 'units' not in config:
            config['units'] = {}
        config['units']['temperature'] = unit

    #
    # PAR FILTERING
    #
    def get_par_filtering(self):
        config = self.load_config()
        return config.get('par_filter', False)
    
    def set_par_filtering(self, config, enabled: bool):
        print("Updating PAR filtering")
        config['par_filter'] = enabled

    #
    # FILEPATH
    #
    def get_default_filepath(self):
        config = self.load_config()
        if 'default_path' in config:
            return config['default_path']
        
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, "Apogee", "apogee_connect_rpi", "data")

    def set_default_filepath(self, config, path: str):
        print("Updating default filepath")
        filepath = self.validate_filepath(path)
        if not filepath:
            raise ValueError("Invalid filepath")

        config['default_path'] = filepath
    
    def validate_filepath(self, filepath):
        # Ensure just filepath is provided, not a filename as well
        if not filepath or os.path.basename(filepath):
            return None
        
        filepath = os.path.normpath(filepath)        

        # Check absolute vs relative filepath
        if os.path.isabs(filepath):
            return filepath
        else:
            return os.path.join(os.getcwd(), filepath)