from .utils import load_config_from_file, update_config_file, format_out_path, get_current_date, get_current_time, rotate_logs
from .dictionaries import log_prefixes, log_headers
import json
import os


class Configure:
    @classmethod
    def display(cls):
        """Displays the current configuration in a formatted JSON structure."""
        config_data = load_config_from_file()
        if config_data:
            print(json.dumps(config_data, indent=4))
        else:
            print("No configuration found.")

    @classmethod
    def set_log_folder_path(cls, path=None):
        """Sets the log folder path and updates the configuration."""

        if isinstance(path, str):
            if not os.path.exists(path):
                os.makedirs(path)

        update_config_file('log_folder', path)

    @classmethod
    def set_log_file_max_size(cls, max_size: int):
        """Sets the maximum log file size in megabytes and updates the configuration."""
        max_size = int(max_size)
        update_config_file('max_size_in_mega_bytes', max_size)

    @classmethod
    def enable_log_rotation(cls, value: bool):
        """Enables or disables log rotation in the configuration."""
        update_config_file('log_rotation', value)


class Logger:
    def __init__(self, log_name=None, log_level=None, log_entry=None, verbose=None):
        self.prefix = log_prefixes.get(log_level, '[INFO]')
        self.path = format_out_path(log_name) if log_name else None
        self.entry = log_entry or ''
        self.verbose = verbose

    def log(self):
        """Logs the entry to the specified log file with optional rotation."""

        message = f'{self.prefix} {get_current_date()} {get_current_time()}: {self.entry}\n'

        try:
            if not self.path:
                print(message)
                return

            if self.verbose:
                print(message)

            if not os.path.exists(self.path):
                self.create_default_log(self.path)

            if load_config_from_file('log_rotation'):
                rotate_logs()

            with open(self.path, 'a') as file:
                file.write(message)

        except IOError as e:
            print(f"Failed to write to log file: {e}")

    @classmethod
    def create_default_log(cls, path):
        """Creates a default log file with a standard header."""
        try:
            with open(path, 'w') as file:
                file.write(log_headers.get('default', "# Log File #\n"))

        except IOError as e:
            print(f"Failed to create log file: {e}")
