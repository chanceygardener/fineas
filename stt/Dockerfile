FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
        && apt-get install libportaudio2 libportaudiocpp0 portaudio19-dev libasound-dev libsndfile1-dev -y

RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "./server.py"]