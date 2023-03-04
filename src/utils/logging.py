import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def log_delivery_message(err, msg):
    if err:
        logging.error(f"Failed to deliver message: {msg.value()}: {err.str()}")
    else:
        logging.info(
            f"Message Produced!\n"
            + f"Topic: {msg.topic()} \n"
            + f"Partition: {msg.partition()} \n"
            + f"Offset: {msg.offset()} \n"
            + f"Timestamp: {msg.timestamp()} \n"
        )
