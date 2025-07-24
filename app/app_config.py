import os
import sys
import typing

def getConfig(path: str) -> typing.Dict[str, typing.Union[str, float, int, bool]]:
    # Helper functions to detect and convert the type
    def is_int(value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False

    def is_float(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    def convert_value(key: str, value: str):
        if key.startswith(("enable_", "remove_", "use_", "clear_")):
            return bool(int(value))
        elif is_int(value):
            return int(value)
        elif is_float(value):
            return float(value)
        else:
            return value

    config = {}
    with open(path, 'r') as file:
        for line in file:
            key_value = line.strip().split(": ", maxsplit=1)
            key = key_value[0]
            value = key_value[1] if len(key_value) > 1 else ""
            config[key] = convert_value(key, value.strip())
    return config

