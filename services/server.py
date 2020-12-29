#!/usr/bin/env/python3

from flask import Flask, jsonify, request
from wolfram import client as wolfram_client
from weather import get_weather, decode_response as decode_weather
from lights import LightManager
from dotenv import load_dotenv
import os

load_dotenv()

light_manager = LightManager(os.getenv("LIGHT_MAP_FILE"))
app = Flask("fineasExternalServices")


@app.route('/wolfram', methods=["POST"])
def wolfram():
    assert request.method == "POST"
    response = extract_wolfram_answer(
        wolfram_client.query(request.form["text"]))
    return jsonify({"response": response})


@app.route('/weather', methods=["POST"])
def weather():
    assert request.method == "POST"
    return jsonify(get_weather(
        request.form["city_name"]))


@app.route('/lights', methods=["POST"])
def lights():
    group_name = request.form["light_group"]
    action = request.form["action"]
    result_state = light_manager[
        group_name].applyCondition(action)
    return jsonify(result_state)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8800)
