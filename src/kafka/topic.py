import os
import sys

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaException
from dotenv import load_dotenv

sys.path.append(".")
from src.utils.config import config_loader

load_dotenv()


def run(config: dict):
    topics = [
        NewTopic(os.environ["TOPIC_NAME"], int(os.environ["TOPIC_PARTITIONS"]), int(os.environ["TOPIC_REPLICAS"]))
    ]
    admin_client = AdminClient(config)

    fs = admin_client.create_topics(topics)

    for topic, future in fs.items():
        try:
            future.result()
            print(f"Topic created: {topic}")
        except KafkaException as e:
            print(e)
            exit(1)
        except Exception as e:
            print(f"Failed to create topic: {topic} ({e})")
            exit(1)


if __name__ == "__main__":
    config_topic = config_loader("config/topic.yml")
    run(config_topic.as_dict())
