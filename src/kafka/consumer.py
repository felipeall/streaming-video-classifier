import sys
from dataclasses import dataclass

import cv2
import numpy as np
from confluent_kafka import Consumer
from keras.applications import ResNet50
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.resnet import preprocess_input

sys.path.append(".")
from src.utils.config import config_loader
from src.utils.mongo import connect_mongo_db
from src.utils.utils import check_message_errors


@dataclass
class KafkaConsumer:
    config_consumer: dict
    config_model: dict

    def __post_init__(self):
        self.consumer = Consumer(**self.config_consumer)
        self.consumer.subscribe(["streaming-video-processing"])
        self.model = ResNet50(
            include_top=config_model.include_top,
            weights=config_model.weights,
            input_tensor=config_model.input_tensor,
            input_shape=config_model.input_shape,
            pooling=config_model.pooling,
            classes=config_model.classes,
        )
        self.mongo_db = connect_mongo_db()

    def run(self):
        print(f"Watching for messages...")
        try:
            while True:
                message = self.consumer.poll(3)

                if check_message_errors(message):
                    continue

                # get metadata
                frame_no = str(message.timestamp()[1])
                video_name = message.headers()[0][1].decode("utf-8")

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
                db_collection = self.mongo_db[video_name]
                if db_collection.find_one({"frame": frame_no}) is None:  # no duplicates
                    document = {"frame": frame_no, "label": top_label, "confidence": confidence}
                    db_collection.insert_one(document)
                    print(f"[{video_name}] Document added to db! {document}")
                else:
                    print(f"[{video_name}] Frame already exists in db: {frame_no}")
                    continue

        finally:
            self.consumer.close()


if __name__ == "__main__":
    config_consumer = config_loader("config/consumer.yml")
    config_model = config_loader("config/resnet50.yml")

    consumer = KafkaConsumer(config_consumer.as_dict(), config_model)
    consumer.run()
