#!/usr/bin/env python3


from typing import Any, Text, Dict, List
import asyncio
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted
import random
from datetime import datetime
import requests
from apiclient import APIClient, endpoint
from dotenv import load_dotenv
import os

load_dotenv()

EXTERNAL_SERVICES_PORT = os.getenv("SERVICES_PORT")
TTS_PORT = os.getenv("TTS_PORT")
TTS_SERVER_ADDRESS = f"http://0.0.0.0:{TTS_PORT}/speak"


class ServicesClient(APIClient):
    base_endpoint = f"http://0.0.0.0:{EXTERNAL_SERVICES_PORT}"

    @endpoint(base_url=base_endpoint)
    class WeatherEndPoint:
        resource = "weather"

    @endpoint(base_url=base_endpoint)
    class LightsEndPoint:
        resource = "lights"

    def set_light_state(self, state, group_name):
        # TODO: define procedure for translating
        # entity reference to desired state
        # into kasa smartbulb method
        # action = get_bulb_method(state)
        return self.post(self.LightsEndPoint.resource,
                         data={
                             "light_group": group_name,
                             "action": f"turn_{state}"
                         })

    def weather_report(self, city):
        return self.post(self.WeatherEndPoint.resource,
                         data={"city_name": city})


services = ServicesClient()


def tts(text):
    r = requests.post(TTS_SERVER_ADDRESS,
                      data={
                          "text": text
                      })
    return r.ok


def generate_response_template():
    return {
        "events": [],
        "responses": []
    }


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        out = generate_response_template()
        dispatcher.utter_message("hello world")

        return out


class ActionGetWeather(Action):

    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        out = generate_response_template()
        city = tracker.get_slot("city")
        assert city
        weather_resp = services.weather_report(city)
        c_weather = weather_resp[0]
        if c_weather == "AMBIGUOUS":
            dispatcher.utter_message(f"Looks like there are a few cities named {city}, which one are you talking about?")
            return out
        elif c_weather == "NOT_FOUND":
            dispatcher.utter_message(f"I don't have any knowledge of {city}")
        else:
            temp_kelvin = c_weather["main"]["temp"]
            temp_fahren = (temp_kelvin - 273.15) * 9/5 + 32
            desc = c_weather["weather"]["description"]
            dispatcher.utter_message(
                f"In {city}, it's {temp_fahren} degrees fahrenheit, with {desc}."
            )


class ActionTellTime(Action):

    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now()
        as_string = now.strftime("%H:%M %p")
        response_message = random.choice([
            f"It's {as_string} right now",
            f"At the moment, it's {as_string}"
        ])
        out = generate_response_template()
        dispatcher.utter_message(text=response_message)

        return out


class ActionToggleLight(Action):

    def name(self) -> Text:
        return "action_toggle_light"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        response_message = ""
        intent = tracker.latest_message['intent'].get('name')
        print(f"Responding to intent: {intent}")
        group_name = tracker.get_slot("which_light")
        desired_state = tracker.get_slot("desired_state")
        print(f"GROUP NAME: {group_name}")
        print(f"DESIRED STATE: {desired_state}")

        if not group_name:
            response_message = random.choice([
                "All of them?",
                "You want me to turn them all off?",
                "Any lights in particular?"
            ])
            # dispatcher.utter_message(response_message)
        elif not desired_state:
            response_message = f"What did you want me to do with the {group_name} lights?"
        else:
            resp = services.set_light_state(
                desired_state, group_name)
            print(f"\nServices endpoint responded with code: {resp.status_code}")
            rdat = resp.json()
            print(rdat)
            ok = resp.json()["ok"]
            singular_light = rdat["num_lights"] == 1
            if ok:
                response_message = f"Ok, I've turned {'it' if singular_light else 'them'} {desired_state}"
            else:
                response_message = "Looks like something might have gone wrong there"
        out = generate_response_template()
        if response_message:
            dispatcher.utter_message(text=response_message)
        return [ActionExecuted(self.name())]
