import yaml

def read_config(file_path):
    with open(file_path) as stream:
        try:
            configs = yaml.safe_load(stream)
            return configs
        except yaml.YAMLError as exc:
            print(exc)

