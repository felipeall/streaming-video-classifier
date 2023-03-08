import concurrent.futures
import logging
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
from confluent_kafka import Producer
from utils import get_videos_paths, load_config_yml, log_delivery_message

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@dataclass
class KafkaProducer:
    config_producer: dict
    videos_paths: list

    def __post_init__(self):
        self._create_producer()

    def _create_producer(self):
        try:
            logging.info(f"Connecting to Kafka server...")
            logging.info(f"Kafka Producer config: {self.config_producer}")
            self.producer = Producer(self.config_producer)
            logging.info(f"Connected to Kafka Server @ {self.config_producer.get('bootstrap.servers')}")
        except Exception as e:
            logging.exception(
                f"Error connecting to Kafka Server @ {self.config_producer.get('bootstrap.servers')} ({e})"
            )
            raise

    def run(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.produce, self.videos_paths)

        self.producer.flush()

    def produce(self, video_path: str):
        logging.info(f"Processing video: {video_path} ...")
        video_name = str(Path(video_path).stem)
        video = cv2.VideoCapture(video_path)
        frame_no = 1
        try:
            while video.isOpened():
                success, frame = video.read()

                if not success:
                    logging.exception(f"Invalid video file: {video_path}")
                    raise SystemExit(f"Invalid video file: {video_path}")

                _, buffer = cv2.imencode(".jpg", frame)

                self.producer.produce(
                    topic="streaming-video-classifier",
                    value=buffer.tobytes(),
                    on_delivery=log_delivery_message,
                    timestamp=frame_no,
                    headers={"video_name": video_name},
                )
                self.producer.poll(0)
                time.sleep(0.2)
                frame_no += 1

        except Exception as e:
            logging.exception(f"Error producing message frames for video: {video_name} ({e})")
            raise

        finally:
            video.release()

        logging.info(f"Finished producing message frames for video: {video_name}")


if __name__ == "__main__":
    logging.info("Starting Kafka Producer...")
    videos_paths = get_videos_paths(folder="videos")
    config_producer = load_config_yml(file="config/producer.yml")

    producer_thread = KafkaProducer(config_producer, videos_paths)
    producer_thread.run()
