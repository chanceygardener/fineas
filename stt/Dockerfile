FROM python:3.8

WORKDIR /app

RUN mkdir /app/models

COPY ./models/*.ppn /app/models/

COPY ./models/*.pbmm /app/models/

COPY ./models/*models.scorer /app/models

COPY requirements.txt .

RUN apt-get update \
        && apt-get install libportaudio2 libportaudiocpp0 portaudio19-dev libasound-dev libsndfile1-dev -y

RUN pip install -r requirements.txt

COPY *.py /app/

CMD ["python", "./server.py"]