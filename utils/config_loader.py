import toml


def load_config(config_file):
    try:
        with open(config_file, "r") as f:
            return toml.load(f)
    except Exception as e:
        raise Exception(f"Error loading config file {config_file}: {str(e)}")
