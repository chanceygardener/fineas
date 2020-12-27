#!/usr/bin/env/python3

import wolframalpha
from flask import Flask, jsonify

APP_ID = "H47RA7-3R9U5A67K3"


app = Flask("wolframAlphaClient")

client = wolframalpha.Client(APP_ID)


def extract_answer(wolfram_response):
    return wolfram_response["pod"][0]["subpod"]["plaintext"]


@app.route('/query', methods=["POST"])
def query():
    assert request.method == "POST"
    response = extract_answer(
        client.query(request.form["text"]))
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run()
