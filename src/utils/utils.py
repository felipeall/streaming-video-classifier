import glob

import cv2


def get_videos_paths(folder: str = "videos", extensions: tuple = ("avi", "mp4", "webm")):
    videos_paths = [file for file in glob.glob(f"{folder}/**", recursive=True) if file.split(".")[-1] in extensions]

    if not videos_paths:
        raise FileNotFoundError(f"No videos files found in folder: {folder}")

    return videos_paths


def serialize_img(img):
    _, img_buffer_arr = cv2.imencode(".jpg", img)
    img_bytes = img_buffer_arr.tobytes()
    return img_bytes
