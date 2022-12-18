#!/usr/bin/env python3

# python3 -m pip install openvr
# License: BSD-3.0 (requires showing notice in binary distributions)
import openvr as vr
import time

EVENT_NONE = 0
EVENT_RISING_EDGE = 1
EVENT_FALLING_EDGE = 2

class SessionState:
    def __init__(self):
        self.system = vr.init(vr.VRApplication_Background)
        self.last_packet = 0
        # Whether the configured input event is high or low.
        self.event_high = False

# Checks if the given button on the given controller is pressed.
# Defaults to joystick click / left hand.
# Returns three values:
#   0 - button not pressed
#   1 - button rising edge
#   2 - button falling edge
def pollButtonPress(
        session_state: SessionState,
        controller: vr.ETrackedControllerRole = vr.TrackedControllerRole_LeftHand,
        button: vr.EVRButtonId = vr.k_EButton_Axis0
        ) -> int:
    lh_idx = session_state.system.getTrackedDeviceIndexForControllerRole(vr.TrackedControllerRole_LeftHand)
    #print("Left hand device idx: {}".format(lh_idx))

    got_state, state = session_state.system.getControllerState(lh_idx)
    if not got_state:
        return EVENT_NONE

    if state.unPacketNum == session_state.last_packet:
        return EVENT_NONE

    # Clicking joysticks and moving joysticks fire the same events. To
    # differentiate movement from clicking, we create a dead zone: if the event
    # fires while the stick isn't moved far from center, we assume it's a
    # click, not movement.
    dead_zone_radius = 0.5

    # This is the ID of event for the joystick being clicked.
    joy_click = vr.k_EButton_Axis0
    joy_click_mask = (1 << joy_click)
    ret = EVENT_NONE
    if (state.ulButtonPressed & joy_click_mask) != 0 and\
            (state.rAxis[0].x**2 + state.rAxis[0].y**2 < dead_zone_radius**2):
        #print("button pressed: %016x" % state.ulButtonPressed)
        #for i in range(0, 5):
        #    print("axis {} x: {} y: {}".format(i, state.rAxis[i].x, state.rAxis[i].y))
        if not session_state.event_high:
            ret = EVENT_RISING_EDGE
        session_state.event_high = True
    elif session_state.event_high:
        session_state.event_high = False
        ret = EVENT_FALLING_EDGE
    return ret

if __name__ == "__main__":
    session_state = SessionState()
    while True:
        time.sleep(0.1)

        event = pollButtonPress(session_state)
        if event == EVENT_RISING_EDGE:
            print("rising edge")
        elif event == EVENT_FALLING_EDGE:
            print("falling edge")

