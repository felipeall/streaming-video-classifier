import sys
from dataclasses import dataclass

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaException

sys.path.append(".")
from src.utils.config import config_loader


@dataclass
class Topic:
    config: dict

    def run(self):
        topics = [NewTopic("streaming-video-processing", 1, 1)]
        admin_client = AdminClient(self.config)

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

    topic = Topic(config_topic.as_dict())
    topic.run()
