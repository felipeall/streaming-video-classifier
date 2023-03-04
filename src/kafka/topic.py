from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaException

from src.utils.config import config_loader


def main():
    config = config_loader("config/topic.yml")

    topics = [NewTopic("streaming-video-processing", config.topic.partitions, config.topic.replicas)]
    admin_client = AdminClient({"bootstrap.servers": config.admin_client.bootstrap.servers})

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
    main()
