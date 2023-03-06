topic:
	python src/kafka/topic.py

producer:
	python src/kafka/producer.py

consumer:
	python src/kafka/consumer.py

terminal:
	docker exec -it kafka bash

topic-count:
	docker exec -it kafka kafka-run-class kafka.tools.GetOffsetShell  --broker-list localhost:9092 --topic streaming-video-classifier
