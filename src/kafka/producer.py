import concurrent.futures
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
from confluent_kafka import Producer

sys.path.append(".")
from src.utils.config import config_loader
from src.utils.logging import log_delivery_message
from src.utils.utils import get_videos_paths


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
        video_name = str(Path(video_path).stem)
        video = cv2.VideoCapture(video_path)
        while video.isOpened():
            success, frame = video.read()

            if not success:
                raise SystemExit(f"Invalid video file: {video_path}")

            _, buffer = cv2.imencode(".jpg", frame)

            self.producer.produce(
                topic="streaming-video-processing",
                value=buffer.tobytes(),
                on_delivery=log_delivery_message,
                headers={"video_name": video_name},
            )
            self.producer.poll(0)
            time.sleep(0.2)

        video.release()
        print(f"Published video: {video_name}")


if __name__ == "__main__":
    videos_paths = get_videos_paths()
    config_producer = config_loader("config/producer.yml")

    producer_thread = ProducerThread(config_producer.as_dict())
    producer_thread.run(videos_paths)
