FROM python:3.9.16-slim-buster

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . /app

CMD ["python3", "src/main.py"]