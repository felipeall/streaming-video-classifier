# Streaming Video Classifier
Kafka project that simulates streaming videos and classifies the frames using [ResNet-50](https://www.tensorflow.org/api_docs/python/tf/keras/applications/resnet50/ResNet50) model


### Running

Clone the repository
````bash
git clone https://github.com/felipeall/streaming-video-classifier.git
````

Access the app root folder
````bash
cd streaming-video-classifier
````

Instantiate the Docker containers (Zookeeper, Kafka and MongoDB)
````bash
docker compose up -d
````

Create Kafka Topic
````bash
make topic
````

Run Kafka Producer and Consumer
````bash
make producer
make consumer
````
