# Load configs from a file 
# Author: derMax450

import json
import os

def load_config(section=None, config_filename='config.json'):
    """
    Load configuration from a JSON file.
    Optionally return a specific section (e.g. 'telegram').

    :param section: Key of the config section to return (optional)
    :param config_filename: Name of the JSON config file
    :return: config dictionary or specific section
    """
    config_path = os.path.join(os.path.dirname(__file__), config_filename)

    try:
        with open(config_path, 'r') as file:
            config = json.load(file)

            if section:
                if section in config:
                    return config[section]
                else:
                    raise KeyError(f"'{section}' section not found in config.")
            return config

    except FileNotFoundError:
        raise FileNotFoundError(f"⚠️ Configuration file '{config_filename}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"⚠️ Configuration file '{config_filename}' is not valid JSON.")
    except KeyError as e:
        raise KeyError(f"⚠️ {e}")
