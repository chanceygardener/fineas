#!/usr/bin/env/python3

import wolframalpha


APP_ID = "H47RA7-3R9U5A67K3"


client = wolframalpha.Client(APP_ID)


def extract_wolfram_answer(wolfram_response):
    return wolfram_response["pod"][0]["subpod"]["plaintext"]

