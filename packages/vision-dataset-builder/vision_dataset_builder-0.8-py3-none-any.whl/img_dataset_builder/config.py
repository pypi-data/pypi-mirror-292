import yaml
import os


def load_config(config_file=None, overrides=None):
    if config_file is None:
        # Adjust path to find `config.yaml` within the package
        config_file = os.path.join(os.path.dirname(__file__), 'config.yaml')

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found.")
    
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    if overrides:
        config.update(overrides)
    
    return config

# Initialize the configuration
config = load_config()
