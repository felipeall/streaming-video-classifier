
minikube:
	@echo "#####################################"
	@echo "##### Starting Minikube Service #####"
	@echo "#####################################"
	minikube start
	@echo "##### Minikube Service OK! #####"

zookeeper:
	@echo "####################################"
	@echo "##### Starting Kafka Zookeeper #####"
	@echo "####################################"
	kubectl apply -f kubernetes/zookeeper.yaml
	@echo "Waiting for 'Ready' condition..."
	@kubectl wait --for=condition=Ready --timeout=600s pod --all
	@echo "##### Kafka Zookeeper OK! #####"

kafka:
	@echo "#################################"
	@echo "##### Starting Kafka Broker #####"
	@echo "#################################"
	kubectl apply -f kubernetes/kafka-broker.yaml
	@echo "Waiting for 'Ready' condition..."
	@kubectl wait --for=condition=Ready --timeout=600s pod --all
	@echo "##### Kafka Broker OK! #####"

mongodb:
	@echo "############################"
	@echo "##### Starting MongoDB #####"
	@echo "############################"
	kubectl apply -f kubernetes/mongodb.yaml
	@kubectl wait --for=condition=Ready --timeout=600s pod --all
	@echo "##### MongoDB OK! #####"

consumer:
	@echo "###################################"
	@echo "##### Starting Video Consumer #####"
	@echo "###################################"
	docker build -t video-consumer -f apps/video-consumer/Dockerfile apps/video-consumer
	minikube image load video-consumer
	kubectl apply -f kubernetes/video-consumer.yaml
	@echo "##### Video Consumer OK! #####"

producer:
	@echo "###################################"
	@echo "##### Starting Video Producer #####"
	@echo "###################################"
	docker build -t video-producer -f apps/video-producer/Dockerfile apps/video-producer
	minikube image load video-producer
	kubectl apply -f kubernetes/video-producer.yaml
	@echo "##### Video Producer OK! #####"

mongodb-local:
	@echo "Forwarding MongoDB port 27017..."
	@echo "Please don't close this terminal!"
	kubectl port-forward service/mongodb-service 27017:27017

kafka-local:
	@echo "Forwarding Kafka Broker port 9093..."
	@echo "Please don't close this terminal!"
	kubectl port-forward service/kafka-broker-service 9093:9093

run: minikube zookeeper kafka mongodb consumer producer
run-kafka: minikube zookeeper kafka
run-producer: minikube zookeeper producer
