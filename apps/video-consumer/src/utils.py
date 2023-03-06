import ast

import yaml


def load_config_yml(config_file_path: str) -> dict:
    config = yaml.safe_load(open(config_file_path))

    config_parsed = {}
    for k, v in config.items():
        if str(v)[0] == "(" and str(v)[-1] == ")":
            config_parsed[k] = ast.literal_eval(str(v))
        elif str(v) == "None":
            config_parsed[k] = None
        else:
            config_parsed[k] = v

    return config_parsed


def check_message_errors(msg):
    if msg is None:
        print("No messages to consume")
        return True
    if msg.error() is not None:
        print(f"Message error: {msg.error()}")
        return True
    else:
        return False
