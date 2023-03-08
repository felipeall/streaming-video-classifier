# Streaming Video Classifier
Project to demonstrate a Kafka deployment in a local Kubernetes environment that simulates streaming videos, 
classifies the frames images using a machine learning model and uploads the predictions to a MongoDB collection

### Technologies

- Docker
- Minikube
- Kafka
- MongoDB
- OpenCV
- Tensorflow

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/): open platform for developing, shipping, and running applications
- [Minikube](https://minikube.sigs.k8s.io/docs/start/): local Kubernetes, focusing on making it easy to learn and develop


### Setup
1. Clone the repository
    ````bash
    https://github.com/felipeall/streaming-video-classifier.git
    ````

2. Put videos files in the following folder:
    ````bash
    streaming-video-classifier/apps/video-producer/videos
    ````
    Supported formats are: `avi`, `mp4` and `webm`

### Running
_tl;dr: `make run`_

1. Start minikube service 
    ````bash
    minikube start
    ````

2. Deploy Zookeeper and Kafka Broker
    ````bash
    kubectl apply -f kubernetes/zookeeper.yaml
    kubectl wait $(kubectl get pods -o name) --for=condition=Ready --timeout=600s
    kubectl apply -f kubernetes/kafka-broker.yaml
    ````

3. Deploy MongoDB
    ````bash
    kubectl apply -f kubernetes/mongodb.yaml
    ````

4. Build and deploy Video Consumer
    ````bash
    docker build -t video-consumer -f apps/video-consumer/Dockerfile apps/video-consumer
    minikube image load video-consumer
    kubectl apply -f kubernetes/video-consumer.yaml
    ````

5. Build and deploy Video Producer
    ````bash
    docker build -t video-producer -f apps/video-producer/Dockerfile apps/video-producer
    minikube image load video-producer
    kubectl apply -f kubernetes/video-producer.yaml
    ````

### Validation

In order to check the output, enable MongoDB port forwarding:

````bash
make mongodb-local
````

And connect to the database locally via:
> mongodb://localhost:27017
