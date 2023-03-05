import os
import sys
import threading
import time
from dataclasses import dataclass, field

import cv2
import numpy as np
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv
from keras.applications import ResNet50
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.resnet import preprocess_input
from keras.engine.functional import Functional
from pymongo.database import Database

sys.path.append(".")
from src.utils.config import config_loader
from src.utils.mongo import (
    connect_mongo_db,
    create_collections_unique,
    insert_data_unique,
)
from src.utils.utils import get_videos_names, reset_map

load_dotenv()


@dataclass
class ConsumerThread:
    config: dict
    batch_size: int
    model: Functional
    db: Database
    videos_mapping: dict
    topic: list = field(default_factory=lambda: [os.environ["TOPIC_NAME"]])

    def run(self, threads):
        for _ in range(threads):
            t = threading.Thread(target=self.read_data)
            t.daemon = True
            t.start()
            while True:
                time.sleep(10)

    def read_data(self):
        consumer = Consumer(self.config)
        consumer.subscribe(self.topic)
        self.execute(consumer, 0, [], [])

    def execute(self, consumer, msg_count, msg_array, metadata_array):
        try:
            while True:
                msg = consumer.poll(0.5)
                if msg is None:
                    continue
                elif msg.error() is None:
                    # convert image bytes data to numpy array of dtype uint8
                    nparr = np.frombuffer(msg.value(), np.uint8)

                    # decode image
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    img = cv2.resize(img, (224, 224))
                    msg_array.append(img)

                    # get metadata
                    frame_no = msg.timestamp()[1]
                    video_name = msg.headers()[0][1].decode("utf-8")

                    metadata_array.append((frame_no, video_name))

                    # bulk process
                    msg_count += 1
                    if msg_count % self.batch_size == 0:
                        # predict on batch
                        img_array = np.asarray(msg_array)
                        img_array = preprocess_input(img_array)
                        predictions = self.model.predict(img_array)
                        labels = decode_predictions(predictions)

                        self.videos_mapping = reset_map(self.videos_mapping)
                        for metadata, label in zip(metadata_array, labels):
                            top_label = label[0][1]
                            confidence = label[0][2]
                            confidence = confidence.item()
                            frame_no, video_name = metadata
                            doc = {"frame": frame_no, "label": top_label, "confidence": confidence}
                            # print(videos_mapping)
                            # exit()
                            self.videos_mapping[video_name].append(doc)

                        # insert bulk results into mongodb
                        insert_data_unique(self.db, self.videos_mapping)

                        # commit synchronously
                        consumer.commit(asynchronous=False)
                        # reset the parameters
                        msg_count = 0
                        metadata_array = []
                        msg_array = []

                elif msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached {msg.topic()}/{msg.partition()}")
                else:
                    print(f"Error occurred: {msg.error().str()}")

        except KeyboardInterrupt:
            print("Interrupted by user. Exiting...")
            pass

        finally:
            consumer.close()


if __name__ == "__main__":
    config_consumer = config_loader("config/consumer.yml")
    config_model = config_loader("config/resnet50.yml")

    model = ResNet50(
        include_top=config_model.include_top,
        weights=config_model.weights,
        input_tensor=config_model.input_tensor,
        input_shape=config_model.input_shape,
        pooling=config_model.pooling,
        classes=config_model.classes,
    )

    db = connect_mongo_db()
    videos_mapping = create_collections_unique(db, get_videos_names())

    consumer_thread = ConsumerThread(config_consumer.as_dict(), 32, model, db, videos_mapping)
    consumer_thread.run(3)
