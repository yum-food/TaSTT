import keyboard
import time

class KeybindEventMachine:
    def __init__(self, keybind: str):
        self.keybind = keybind
        self.events = []
        keyboard.add_hotkey(keybind, self.onPress)

    def onPress(self) -> None:
        self.events.append(time.time())

    # Returns the timestamp when the keybind was pressed, or 0 if no keypresses
    # are queued.
    def getNextPressTime(self) -> int:
        if len(self.events) == 0:
            return 0
        ret = self.events[0]
        self.events = self.events[1:]
        return ret

