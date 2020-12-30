FROM rasa/rasa-sdk:2.2.0

WORKDIR /app

COPY ./models /app

EXPOSE 5005:5005

CMD ["rasa", "run", "--enable-api"]
