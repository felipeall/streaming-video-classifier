import glob
from pathlib import Path


def get_videos_paths(folder: str = "videos", extensions: tuple = ("avi", "mp4", "webm")):
    videos_paths = [file for file in glob.glob(f"{folder}/**", recursive=True) if file.split(".")[-1] in extensions]

    if not videos_paths:
        raise FileNotFoundError(f"No videos files found in folder: {folder}")

    return videos_paths


def get_videos_names(folder: str = "videos"):
    videos_paths = get_videos_paths(folder=folder)

    return [Path(video).stem for video in videos_paths]


def check_message_errors(msg):
    if msg is None:
        print("No messages to consume")
        return True
    if msg.error() is not None:
        print(f"Message error: {msg.error()}")
        return True
    else:
        return False
