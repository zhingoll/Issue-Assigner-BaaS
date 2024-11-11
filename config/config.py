import os

class ModelConf():
    def __init__(self, file_path):
        self.config = {}
        self.read_configuration(file_path)

    def __getitem__(self, item):
        try:
            return self.config[item]
        except KeyError:
            raise ValueError(f'Parameter {item} is not found in the configuration file!')

    def read_configuration(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError('Config file is not found!')

        with open(file_path, 'r') as f:
            for ind, line in enumerate(f, 1):  # ind starting from 1, more intuitive
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    try:
                        key, value = line.split('=', 1)  # Only split at the first '='
                        key = key.strip()
                        value = value.strip()
                        self.config[key] = self.parse_value(value)
                    except ValueError:
                        raise ValueError(f'Config file is not in the correct format! Error Line: {ind}')

    def parse_value(self, value):
        """ Parses the value to int, float, str, or dictionary, handling lists as well. """
        if ',' in value:
            values = value.split(',')
            parsed_values = [self.parse_single_value(v.strip()) for v in values]
            # Check if values contain 'key value' pairs
            if all(' ' in v for v in values):
                return {v.split(' ')[0]: self.parse_single_value(v.split(' ')[1]) for v in values}
            return parsed_values
        else:
            return self.parse_single_value(value)

    def parse_single_value(self, value):
        """ Converts a single string value to int, float or str. """
        try:
            # Try converting to int
            return int(value)
        except ValueError:
            try:
                # Try converting to float
                return float(value)
            except ValueError:
                # Return string as is
                return value
