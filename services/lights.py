#!/usr/bin/env python3

"""Summary

Attributes:
    BULB_MAP_PATH (str): Description
    office (TYPE): Description
"""

from kasa.smartbulb import SmartBulb
import json
import asyncio
import random
import time
from sys import exc_info

BULB_MAP_PATH = "utils/homeautomation/bulb_map.json"


def read_json(mpath):
    """Summary
    
    Args:
        mpath (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    with open(mpath) as mfile:
        BULB_MAP = json.loads(mfile.read())
    return BULB_MAP


class LightGroup(list):

    """Summary
    """
    
    def __init__(self, ips):
        """Summary
        
        Args:
            ips (TYPE): Description
        """
        super().__init__(self)
        self += list(map(
            self._get_initial_bulb_data,
            ips))


    def _get_initial_bulb_data(self, ip):
        """Summary
        
        Args:
            ip string: The ip address of a smart bulb
        
        Returns:
            SmartBulb: a kasa SmartBulb object corresponding to the IP
        """
        bulb = SmartBulb(ip)
        asyncio.run(bulb.update())
        return bulb

    def _is_condition(self, condition_method):
        """Summary
        
        Args:
            condition_method (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        return all(map(lambda b: getattr(SmartBulb,
             condition_method)(b), self))

    def isOn(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._is_condition("is_on")

    def isOff(self):
        return self._is_condition("is_off")

    def applyCondition(self, action):
        """apply a method to change the state
        of each bulb in the group
        
        Args:
            group_name (TYPE): Description
            action (TYPE): Description
        """
        action = getattr(SmartBulb, action)
        result_state = {
            "errs": {}
        }
        for bulb in self:
            try:
                res = asyncio.run(action(bulb))
            except Exception as e:
                result_state["errs"][bulb.alias] = f"{type(e): {e.args[0]}}" 
                print(exc_info())
        result_state["ok"] = not bool(result_state["errs"])
        result_state['num_lights'] = len([bulb for bulb in self])
        print(f"light state transition report for {action}")
        print(result_state)
        return result_state

    




class LightManager:
    
    def __init__(self, map_path):
        groups = read_json(map_path)
        self._groups = {groupName: LightGroup(groups[groupName])
                        for groupName in groups}

    def __getitem__(self, key):
        """Summary
        
        Args:
            key (TYPE): Description
        
        Raises:
            ValueError: Description
        """
        assert isinstance(key,
                          str), f"LightManager lookup keys should be string, got {type(key)}"
        val = self._groups.get(key)
        if val is None:
            raise ValueError(f"Group {key} not found, check light map file")
        return val

    


        


office = SmartBulb("192.168.86.122")
asyncio.run(office.update())


def chaos(bulb):
    """Summary
    
    Args:
        bulb (TYPE): Description
    """
    asyncio.run(office.set_hsv(random.choice(range(0, 200)),
                               random.choice(range(0, 100)),
                               random.choice(range(0, 100))))
    #time.sleep(random.choice(range(1, 5)))


if __name__ == "__main__":
    while True:
        chaos(office)
