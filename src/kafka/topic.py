import sys
from dataclasses import dataclass

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaException

sys.path.append(".")
from utils.utils import load_config_yml


@dataclass
class Topic:
    config_topic: dict
    config_admin_client: dict

    def run(self):
        topics = [NewTopic("streaming-video-processing", config_topic.get("partitions"), config_topic.get("replicas"))]
        admin_client = AdminClient(self.config_admin_client)

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
    config_topic = load_config_yml("config/topic.yml")
    config_admin_client = load_config_yml("config/admin_client.yml")

    topic = Topic(config_topic, config_admin_client)
    topic.run()
