#!/usr/bin/env python3

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
import asyncio
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import kasa, random
from datetime import datetime


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
        dispatcher.utter_message(text="Hello World!")

        return out

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

        bulb_ids = tracker.get_slot("which_lights")
        if not bulb_ids:
            response_message = random.choice([
                    "All of them?",
                    "You want me to turn them all off?",
                    "Any lights in particular?"
                ])
            dispatcher.utter_message(response_message)
        else:
            desired_state = dispatcher.get_slot("desired_state")
            # So, True for on and False for off.
            desired_state = (desired_state == "on")
            bulbs, states = [], []

            for bid in bulb_ids:
                bulb = kasa.SmartBulb(bid)
                bulb.update()
                # get current bulb state
                bulbs.append(bulb)
                states.append(bulb.is_on)
            if not all(state is desired_state for state in states):
                desired_state_word = "on" if desired_state else "off"
                current_state_word = "off" if desired_state else "on"
                response_message = random.choice([
                        f"It looks like not all of those are {current_state_word}, would you like me to turn them all {desired_state_word}?",
                        f"I don't think all of those lights are {current_state_word} at the moment, would you like me to turn them all {desired_state_word}?"
                    ])

        out = generate_response_template()
        if response_message:
            dispatcher.utter_message(text=response_message)
        return out
