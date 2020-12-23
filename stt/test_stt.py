#!/usr/bin/env python3

import pyaudio
from deepspeech import Model
import scipy.io.wavfile as wav
import wave, struct

MODEL_PATH = "/home/chanceygardener/projects/fineas/stt/models/deepspeech-0.9.3-models.pbmm"

WAVE_OUTPUT_FILENAME = "test_audio.wav"

def record_audio(WAVE_OUTPUT_FILENAME):
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 16000
	RECORD_SECONDS = 5

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

	print("* recording")

	frames = [stream.read(CHUNK) for i in range(0, int(RATE / CHUNK * RECORD_SECONDS))]

	print("* done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()


def deepspeech_predict(WAVE_OUTPUT_FILENAME):


	ds = Model(MODEL_PATH)

	fs, audio = wav.read(WAVE_OUTPUT_FILENAME)
	print(f"type of variable: fs -> {type(fs)}")
	return ds.stt(audio)

if __name__ == '__main__':
	record_audio(WAVE_OUTPUT_FILENAME)
	predicted_text = deepspeech_predict(WAVE_OUTPUT_FILENAME)
	print(predicted_text)