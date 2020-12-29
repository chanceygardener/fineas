#!/usr/bin/env python3

import requests
from os import getenv
import json

key = getenv("OPEN_WEATHER_API_KEY")
city_lookup_path = getenv("OPEN_WEATHER_CITY_LOOKUP_MAP")

assert key is not None

endpoint = "http://api.openweathermap.org/data/2.5/weather"



def lookup_city_id(city_name):
	with open(city_lookup_path) as mapfile:
		table = json.loads(mapfile.read())
		possible = [c["id"] for c in table if c["name"].lower() == city_name.lower()]
	return possible

def get_weather(city_name):
	possible = lookup_city_id(city_name)
	if len(possible) == 1:
		city_id = possible[0]
		query = f"?id={city_id}&appid={key}"
		response = requests.get(endpoint + query)
		return response
	elif not possible:
		return ["NOT_FOUND"]
	else:
		return ["AMBIGUOUS"]

def test_weather(city_name):
	possible = lookup_city_id(city_name)
	print(f"Found {len(possible)} cities with the name {city_name}")
	city_id = possible[0]
	query = f"?id={city_id}&appid={key}"
	response = requests.get(endpoint + query)
	return response

def decode_response(struct, weather_key="description"):
	return struct["weather"][0][weather_key]


