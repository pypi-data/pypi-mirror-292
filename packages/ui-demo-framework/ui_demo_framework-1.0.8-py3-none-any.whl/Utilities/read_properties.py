import configparser
import os
from typing import Type, Any


class ReadConfig:
    def __init__(self, config_file='../Configuration/config.ini'):
        self.config = configparser.ConfigParser()
        self.config_file = os.path.join(os.path.dirname(__file__), config_file)
        self.config.read(self.config_file)
        self.details = os.getenv("ENV", "DEFAULT")

        if self.details not in self.config:
            raise ValueError(f"Environment {self.details} not found in configuration.")

    def get_value(self, section: str, key: str, default: Any = None, data_type: Type = str):
        """
        Retrieves a value from the configuration file.

        Args:
        - section: Section name in the config file.
        - key: Key within the section.
        - default: Default value to return if key is not found (default: None).
        - data_type: Data type to convert the value to (default: str).

        Returns:
        - The value from the config file, converted to the specified data type.
        """
        try:
            value_str = self.config.get(section, key)
            return data_type(value_str)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if default is not None:
                return default
            raise ValueError(f"Config key '{key}' not found in section '{section}'.")

    def get_delay_implicit(self):
        return self.get_value(self.details, 'delay_implicit', data_type=int)

    def get_delay_web_element(self):
        return self.get_value(self.details, 'delay_web_element', data_type=int)

    def get_url(self):
        return self.get_value(self.details, 'url')

    def get_email_details(self):
        return {
            'host': self.get_value(self.details, 'host'),
            'username': self.get_value(self.details, 'username'),
            'password': self.get_value(self.details, 'password')
        }

    def get_bluemail_details(self):
        return {
            'host': self.config.get(self.details, 'bluemail_host'),
            'username': self.config.get(self.details, 'bluemail_username'),
            'password': self.config.get(self.details, 'bluemail_password')
        }

    def get_to_email_contacts(self):
        return self.get_value(self.details, 'to_contacts')
