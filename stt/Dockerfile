FROM python:3.8

WORKDIR /app

RUN mkdir /app/models

COPY download_model.sh /app

RUN ./download_model.sh

COPY requirements.txt .

RUN apt-get update \
        && apt-get install libportaudio2 libportaudiocpp0 portaudio19-dev libasound-dev libsndfile1-dev -y

RUN pip install -r requirements.txt

COPY *.py /app/

CMD waitress-serve server:app