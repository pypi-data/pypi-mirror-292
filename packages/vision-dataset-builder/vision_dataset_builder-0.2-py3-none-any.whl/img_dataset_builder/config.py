import yaml


def load_config(config_file="config.yaml", overrides=None):
    with open(config_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    if overrides:
        config.update(overrides)
    
    return config

# Initialize the configuration
config = load_config()
