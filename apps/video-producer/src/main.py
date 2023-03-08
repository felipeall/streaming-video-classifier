import concurrent.futures
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
from confluent_kafka import Producer
from utils import get_videos_paths, load_config_yml, log_delivery_message


@dataclass
class ProducerThread:
    config: dict
    videos_paths: list

    def __post_init__(self):
        self.producer = Producer(self.config)

    def run(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.produce, self.videos_paths)

        self.producer.flush()

    def produce(self, video_path: str):
        video_name = str(Path(video_path).stem)
        video = cv2.VideoCapture(video_path)
        frame_no = 1
        try:
            while video.isOpened():
                success, frame = video.read()

                if not success:
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
            print(f"Error! {e}")
            raise

        finally:
            video.release()

        print(f"Published video: {video_name}")


if __name__ == "__main__":
    videos_paths = get_videos_paths(folder="videos")
    config_producer = load_config_yml(file="config/producer.yml")

    producer_thread = ProducerThread(config_producer, videos_paths)
    producer_thread.run()
