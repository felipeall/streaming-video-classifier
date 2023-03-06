import ast
import glob
import logging

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def log_delivery_message(err, msg):
    if err:
        logging.error(f"Failed to deliver message: {msg.value()}: {err.str()}")
    else:
        logging.info(
            f"Message Produced!\n"
            + f"Topic: {msg.topic()} \n"
            + f"Partition: {msg.partition()} \n"
            + f"Offset: {msg.offset()} \n"
            + f"Timestamp: {msg.timestamp()} \n"
        )


def load_config_yml(file: str) -> dict:
    config = yaml.safe_load(open(file))

    config_parsed = {}
    for k, v in config.items():
        if str(v)[0] == "(" and str(v)[-1] == ")":
            config_parsed[k] = ast.literal_eval(str(v))
        elif str(v) == "None":
            config_parsed[k] = None
        else:
            config_parsed[k] = v

    return config_parsed


def get_videos_paths(folder: str, extensions: tuple = ("avi", "mp4", "webm")):
    videos_paths = [file for file in glob.glob(f"{folder}/**", recursive=True) if file.split(".")[-1] in extensions]

    if not videos_paths:
        raise FileNotFoundError(f"No videos files found in folder: {folder}")

    return videos_paths
