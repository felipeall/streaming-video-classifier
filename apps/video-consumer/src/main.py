import logging
import os
from dataclasses import dataclass

import cv2
import numpy as np
from confluent_kafka import Consumer
from keras.applications import ResNet50
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.resnet import preprocess_input
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from utils import check_message_errors, load_config_yml

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@dataclass
class KafkaConsumer:
    config_consumer: dict
    config_model: dict

    def __post_init__(self):
        self._validate_args()
        self._instantiate_model()
        self._connect_mongodb()
        self._create_consumer()

    def _validate_args(self):
        self.config_mongodb = os.getenv("MONGODB_CONN_URI")
        if not self.config_mongodb:
            logging.critical("Missing `MONGODB_CONN_URI` environment variable!")
            raise SystemExit("Missing `MONGODB_CONN_URI` environment variable!")

        self.bootstrap_server = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        if self.bootstrap_server is None:
            logging.critical("Missing `KAFKA_BOOTSTRAP_SERVERS` environment variable!")
            raise SystemExit("Missing `KAFKA_BOOTSTRAP_SERVERS` environment variable!")

        self.kafka_topic = os.getenv("KAFKA_TOPIC_NAME")
        if self.kafka_topic is None:
            logging.critical("Missing `KAFKA_TOPIC_NAME` environment variable!")
            raise SystemExit("Missing `KAFKA_TOPIC_NAME` environment variable!")

    def _instantiate_model(self):
        try:
            logging.info("Instantiating ResNet50 model...")
            logging.info(f"ResNet50 model config: {self.config_model}")
            self.model = ResNet50(**self.config_model)
        except Exception as e:
            logging.exception(f"Error instantiating ResNet50 model ({e})")
            raise

    def _connect_mongodb(self):
        try:
            logging.info("Connecting to MongoDB...")
            logging.info(f"MongoDB config: {self.config_mongodb}")
            client = MongoClient(self.config_mongodb)
            client.server_info()
            self.mongodb = client[self.kafka_topic]
        except ServerSelectionTimeoutError:
            logging.exception(f"Unable to connect to MongoDB @ {self.config_mongodb}")
            raise SystemExit(f"Unable to connect to MongoDB @ {self.config_mongodb}")
        except Exception as e:
            logging.exception(f"Error connecting to MongoDB ({e})")
            raise

    def _create_consumer(self):
        try:
            self.config_consumer["bootstrap.servers"] = self.bootstrap_server
            logging.info(f"Connecting to Kafka server...")
            logging.info(f"Kafka Consumer config: {self.config_consumer}")
            self.consumer = Consumer(**self.config_consumer)
            self.consumer.subscribe([self.kafka_topic])
        except Exception as e:
            logging.exception(f"Error connecting to Kafka Server @ {self.bootstrap_server} ({e})")
            raise

    def run(self):
        logging.info(f"Watching for messages...")
        try:
            while True:
                message = self.consumer.poll(1)

                if check_message_errors(message):
                    continue

                # get metadata
                frame_no = int(message.timestamp()[1])
                video_name = message.headers()[0][1].decode("utf-8")
                video_timestamp_sec = float(message.headers()[1][1].decode("utf-8")) / 1000

                # decode image
                image_msg = np.frombuffer(message.value(), np.uint8)
                image = cv2.imdecode(image_msg, cv2.IMREAD_COLOR)
                image = cv2.resize(image, (224, 224))

                # pre process
                image = np.asarray([image])
                image = preprocess_input(image)

                # run model
                prediction = self.model.predict(image)
                label = decode_predictions(prediction)

                # get results
                top_label = str(label[0][0][1])
                confidence = float(label[0][0][2])

                # mongo db
                db_collection = self.mongodb[video_name]
                if db_collection.find_one({"frame": frame_no}) is None:
                    document = {"frame": frame_no, "timestamp": video_timestamp_sec, "label": top_label, "confidence": confidence}
                    db_collection.insert_one(document)
                    logging.info(f"[{video_name}] Frame label added to database: {document}")
                else:
                    logging.warning(f"[{video_name}] Frame already exists in database: {frame_no}")
                    continue

        except KeyboardInterrupt:
            logging.critical("Interrupted by the user! Exiting Kafka Consumer...")
            pass

        except Exception as e:
            logging.exception(f"Error! {e}")
            raise

        finally:
            self.consumer.close()


if __name__ == "__main__":
    logging.info("Starting Kafka Consumer...")
    config_consumer = load_config_yml("config/consumer.yml")
    config_model = load_config_yml("config/resnet50.yml")

    consumer = KafkaConsumer(config_consumer, config_model)
    consumer.run()
