#!/usr/bin/env python3

# python3 -m pip install openvr
# License: BSD-3.0 (requires showing notice in binary distributions)
import openvr as vr
import sys
import time

EVENT_NONE = 0
EVENT_RISING_EDGE = 1
EVENT_FALLING_EDGE = 2

class InputEvent:
    def __init__(self,
            opcode: int):
        self.opcode = opcode

# Checks if the given button on the given controller is pressed.
def pollButtonPress(
        hand: str = "right",
        button: str = "b",
        ) -> int:
    hands = {}
    hands["left"] = vr.TrackedControllerRole_LeftHand
    hands["right"] = vr.TrackedControllerRole_RightHand

    buttons = {}
    buttons["a"] = vr.k_EButton_IndexController_A
    buttons["b"] = vr.k_EButton_IndexController_B
    buttons["thumbstick"] = vr.k_EButton_Axis0

    system = None
    while not system:
        try:
            system = vr.init(vr.VRApplication_Background)
        except Exception as e:
            print(f"Failed to start steamVR input thread: {repr(e)}", file=sys.stderr)
            time.sleep(5)
    last_packet = 0
    event_high = False

    while True:
        time.sleep(0.01)

        lh_idx = system.getTrackedDeviceIndexForControllerRole(hand_id)
        #print("left hand device idx: {}".format(lh_idx))

        got_state, state = system.getControllerState(lh_idx)
        if not got_state:
            continue

        if state.unPacketNum == last_packet:
            continue

        # Clicking joysticks and moving joysticks fire the same events. To
        # differentiate movement from clicking, we create a dead zone: if the event
        # fires while the stick isn't moved far from center, we assume it's a
        # click, not movement.
        dead_zone_radius = 0.7

        button_mask = (1 << button_id)
        ret = EVENT_NONE
        if (state.ulButtonPressed & button_mask) != 0 and\
                (state.rAxis[0].x**2 + state.rAxis[0].y**2 < dead_zone_radius**2):
            #print("button pressed: %016x" % state.ulButtonPressed)
            #for i in range(0, 5):
            #    print("axis {} x: {} y: {}".format(i, state.rAxis[i].x, state.rAxis[i].y))
            if not event_high:
                yield InputEvent(EVENT_RISING_EDGE)
            event_high = True
        elif event_high:
            event_high = False
            yield InputEvent(EVENT_FALLING_EDGE)

if __name__ == "__main__":
    gen = pollButtonPress()
    while True:
        time.sleep(0.1)

        event = pollButtonPress(session_state, hand_id = hands["left"], button_id = buttons["joystick"])
        if event == EVENT_RISING_EDGE:
            print("rising edge")
        elif event == EVENT_FALLING_EDGE:
            print("falling edge")

