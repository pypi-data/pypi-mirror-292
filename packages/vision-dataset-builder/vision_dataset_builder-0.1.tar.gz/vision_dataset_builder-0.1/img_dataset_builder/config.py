import yaml


def load_config(config_file="config.yaml"):
    with open(config_file, "r" ,encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config


# Load the configuration when the module is imported
config = load_config()
