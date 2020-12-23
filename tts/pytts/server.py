#!/usr/bin/env python3

from flask import Flask, request
import pyttsx3 as tts



app = Flask("TTS")

tts_engine = tts.init()


@app.route('/speak', methods=["POST"])
def speak():
	assert request.method == "POST"
	tts_engine.say(request.form["text"])
	tts_engine.runAndWait()
	return request.form["text"]

if __name__ == "__main__":
	app.run()


