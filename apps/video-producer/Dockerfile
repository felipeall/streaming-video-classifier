FROM python:3.9.16-slim-buster

WORKDIR /app
RUN pip3 install confluent-kafka pyyaml opencv-python-headless
COPY . /app

CMD ["python3", "src/main.py"]