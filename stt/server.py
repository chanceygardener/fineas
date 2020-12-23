#!/usr/bin/env python3

from picovoice.picovoice import pvporcupine
from threading import Thread
from flask import Flask, request
import pyaudio
import json
import requests
import random
from deepspeech import Model
import scipy.io.wavfile as wav
from io import BytesIO
import wave
import struct
import numpy as np
from os import path, getcwd, remove

p = pyaudio.PyAudio()
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
WAKE_WORDS = {"fineas", "test"}
WAKE_WORDS = {"terminator"}
STT_MODEL_PATH = "/home/chanceygardener/projects/fineas/stt/models/deepspeech-0.9.3-models.pbmm"
TTS_SERVER_ADDRESS = "http://0.0.0.0:5000/speak"
NLU_SERVER_ADDRESS = "http://0.0.0.0:5005/model/parse"
ACKNOWLEDGEMENTS = {'what can I do you for?', 'yep?',
                    'can I help you?', 'at your service yo', "what's up?"}


app = Flask("STT_SERVER")


def nlg(intent_name):
    with open("test_response_map.json") as jfile:
        rmap = json.loads(jfile.read())
    if intent_name is None:
        intent_name = "fallback"
    return random.choice(rmap[intent_name])


def record_audio(stream, ofname, tmp_path="tmp"):

    # stream = pa_conn.open(format=FORMAT,
    #                       channels=CHANNELS,
    #                       rate=RATE,
    #                       input=True,
    #                       frames_per_buffer=CHUNK)

    print("* recording NLU input")
    t = stream.read(CHUNK)
    # print(t)
    # print(type(t))
    # raise ValueError("expected")

    frames = [stream.read(CHUNK)
              for i in range(0,
                             int(RATE / CHUNK * RECORD_SECONDS))]

    stream.stop_stream()
    stream.close()
    # pa_conn.terminate()
    WAVE_OUTPUT_FILENAME = path.join(getcwd(), "tmp", ofname)
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # audio = np.frombuffer(audio_bytes).astype(np.int16)
    # #fs, audio = wav.read(BytesIO(audio_bytes))
    # print(audio)
    # print(audio.astype(np.int16))
    # print("* done recording")

    # stream.stop_stream()
    # stream.close()
    # return audio


class WakeWordListener:

    def __init__(self, words, stt_model_path,
                 audio_connection,
                 tts_server=TTS_SERVER_ADDRESS,
                 nlu_server=NLU_SERVER_ADDRESS):
        super(WakeWordListener, self).__init__()
        self.active_words = set(words)
        self._porcupine = pvporcupine.create(
            library_path=pvporcupine.LIBRARY_PATH,
            model_path=pvporcupine.MODEL_PATH,
            keywords=self.active_words
        )
        self.stream = self._init_audio_stream()
        self.audio_connection = audio_connection
        self.target_model = Model(stt_model_path)
        self._tts_server = tts_server
        self._nlu_server = nlu_server

    def _deepspeech_predict(self, wav_fname):
        fs, audio = wav.read(wav_fname)
        out_text = self.target_model.stt(audio)
        print(f"RECOGNIZED TEXT: {out_text}")
        return out_text

    def _init_audio_stream(self):
        return self.audio_connection.open(
            rate=self._porcupine.sample_rate,
            channels=CHANNELS,
            format=FORMAT,
            input=True,
            frames_per_buffer=self._porcupine.frame_length)

    def _request_service(self, addr, dat=None):
        return requests.post(addr, data=dat)

    def _request_tts(self, text):
        self._request_service(self._tts_server, dat={
            "text": text
        })

    def _request_nlu(self, text):
        print("Sending the following text to NLU")
        print(text)
        resp = self._request_service(self._nlu_server,
                                     dat=json.dumps({
                                         "text": text
                                     }))
        return resp

    def run(self):
        stream = self._open_audio_stream()
        print("listening")
        try:
            while True:
                #stream = self._open_audio_stream()
                pcm = stream.read(self._porcupine._frame_length)
                pcm = struct.unpack_from(
                    "h" * self._porcupine.frame_length,
                    pcm)
                result = self._porcupine.process(pcm)
                if result >= 0:
                    print("DETECTED KEYWORD")
                    print(result)
                    # Send request to tts server
                    # to acknowledge to the user
                    # that Fineas is listening
                    self._request_tts(random.choice(
                        list(ACKNOWLEDGEMENTS)))
                    # stop this stream
                    # stream.stop_stream()
                    # stream.close()
                    audio = record_audio(
                        stream, "utterance.wav")
                    utt_tmp_path = path.join(getcwd(), "tmp", "utterance.wav")
                    interpreted_text = self._deepspeech_predict(utt_tmp_path)
                    remove(utt_tmp_path)

                    # TODO: this should be handled by a rasa action
                    # server
                    nlu_resp = self._request_nlu(interpreted_text).json()
                    print("Got this response from NLU")
                    print(nlu_resp)
                    nl_response = nlg(nlu_resp['intent']['name'])
                    print(f"\nResponding with the following:\n{nl_response}\n")
                    self._request_tts(nl_response)
                    stream.stop_stream()
                    stream.close()
                    # self.audio_connection.terminate()
                    # # reopen the stream to listen for wake word
                    # print(p.get_default_input_device_info())
                    stream = self._open_audio_stream()

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            if self._porcupine is not None:
                self._porcupine.delete()
            if stream is not None:
                stream.close()


if __name__ == "__main__":
    listener = WakeWordListener(WAKE_WORDS,
                                STT_MODEL_PATH, p)
    listener.run()