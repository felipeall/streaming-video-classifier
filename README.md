# Streaming Video Classifier
Project to demonstrate a Kafka deployment in a local Kubernetes environment that simulates streaming videos, 
classifies the frames images using a machine learning model and uploads the predictions to a MongoDB collection

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/): open platform for developing, shipping, and running applications
- [Minikube](https://minikube.sigs.k8s.io/docs/start/): local Kubernetes, focusing on making it easy to learn and develop

### Running

Start minikube service
````bash
minikube start
````

Deploy Zookeeper and Kafka Broker
````bash
kubectl apply -f kubernetes/zookeeper.yaml
kubectl wait $(kubectl get pods -o name) --for=condition=Ready --timeout=600s
kubectl apply -f kubernetes/kafka-broker.yaml
````

Deploy MongoDB
````bash
kubectl apply -f kubernetes/mongodb.yaml
````

Build and deploy Video Consumer
````bash
docker build -t video-consumer -f apps/video-consumer/Dockerfile apps/video-consumer
minikube image load video-consumer
kubectl apply -f kubernetes/video-consumer.yaml
````

Build and deploy Video Producer
````bash
docker build -t video-producer -f apps/video-producer/Dockerfile apps/video-producer
minikube image load video-producer
kubectl apply -f kubernetes/video-producer.yaml
````

### Validation

In order to check the output, one can enable MongoDB port forwarding:

````bash
kubectl port-forward service/mongodb-service 27017:27017
````

And connect to the database via localhost:
> mongodb://localhost:27017
