# written by Jeemin Kim
# Jan 15, 2022
# github.com/mrharrykim

from typing import Union
from re import findall

class RoptoError(Exception):
    pass

class TimeOperationNotPermittedError(RoptoError):
    pass

class Time:
    def __init__(self, millisecond: int):
        self.millisecond = millisecond
    def __add__(self, other):
        if not isinstance(other, Time):
            raise TimeOperationNotPermittedError("Only supports addition between routes")
        return Time(self.millisecond + other.millisecond)
    def __format__(self, __format_spec: str) -> str:
        precursor = findall("%(\w)(0?)\[(.*?)\]", __format_spec)
        formatted_string = ""
        for item in precursor:
            value = self.get(item[0])
            if value == 0 and not item[1]:
                continue
            formatted_string += str(value)
            formatted_string += item[2]
        return formatted_string
    def get(self, id: str) -> int:
        if id == "h":
            return self.millisecond//(3_600_000)
        if id == "m":
            return self.millisecond//(60_000)
        if id == "s":
            return self.millisecond//(1000)
        else:
            return None

def get_equivalences(items: Union[list, tuple]) -> list[list[int]]:
    indexs = set(range(len(items)))
    equivalences = []
    while indexs:
        base_index = indexs.pop()
        equivalence = [base_index]
        for index in indexs:
            if items[index] == items[base_index]:
                equivalence.append(index)
        indexs = indexs.difference(equivalence)
        equivalences.append(equivalence)
    return equivalences

def remove_duplicates(items: Union[list, tuple], equivalences: list[list[int]]) -> list:
    for equivalence in equivalences:
        if len(equivalence) > 1:
            for index in equivalence[1:]:
                items[index] = None
    unique_items = [item for item in items if item != None]
    return unique_items

def get_coordinate(geocode: dict) -> str:
    return geocode["x"] + "," + geocode["y"]

def get_duration(direction: dict) -> Union[None, int]:
    if not direction:
        return None
    return direction["summary"]["duration"]
