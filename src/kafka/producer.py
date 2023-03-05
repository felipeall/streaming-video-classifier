import concurrent.futures
import time
from dataclasses import dataclass
from pathlib import Path
import sys

import cv2
from confluent_kafka import Producer

sys.path.append(".")
from src.utils.config import config_loader
from src.utils.logging import log_delivery_message
from src.utils.utils import get_videos_paths, serialize_img


@dataclass
class ProducerThread:
    config: dict

    def __post_init__(self):
        self.producer = Producer(self.config)

    def run(self, videos_paths: list):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.publish_frame, videos_paths)

        self.producer.flush()

    def publish_frame(self, video_path: str):
        video_name = Path(video_path).stem
        video = cv2.VideoCapture(video_path)
        frame_no = 1
        while video.isOpened():
            _, frame = video.read()
            if frame_no % 3 == 0:
                frame_bytes = serialize_img(frame)
                self.producer.produce(
                    topic="streaming-video-processing",
                    value=frame_bytes,
                    on_delivery=log_delivery_message,
                    timestamp=frame_no,
                    headers={"video_name": str.encode(video_name)},
                )
                self.producer.poll(0)
            time.sleep(0.1)
            frame_no += 1
        video.release()


if __name__ == "__main__":
    videos_paths = get_videos_paths()
    config = config_loader("config/producer.yml")

    producer_thread = ProducerThread(config.as_dict())
    producer_thread.run(videos_paths)
