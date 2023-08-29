import openvr
import sys
import time
import typing

EVENT_RISING_EDGE = 0
EVENT_FALLING_EDGE = 1
EVENT_POSE = 2

class InputEvent:
    def __init__(self,
            opcode: int,
            pos: typing.Tuple[float,float,float] = None):
        self.opcode = opcode
        self.pos = pos

    def __str__(self):
        if self.opcode == EVENT_RISING_EDGE:
            return "EVENT_RISING_EDGE"
        elif self.opcode == EVENT_FALLING_EDGE:
            return "EVENT_FALLING_EDGE"
        elif self.opcode == EVENT_POSE:
            return f"EVENT_POSE: {self.pos}"

def pollButtonPress(hand: str = "right", button: str = "b") -> InputEvent:
    openvr.init(openvr.VRApplication_Overlay)

    system = openvr.VRSystem()

    button_mapping = {
        'a': k_EButton_Index_Controller_A,
        'b': k_EButton_Index_Controller_B,
        'thumbstick': k_EButton_SteamVR_Touchpad,
    }

    print("SteamVR session created. Listening for controller input...")

    while True:
        # Drain input events.
        event = openvr.VREvent_t()
        while system.pollNextEvent(event):
            # Event processing, e.g. button presses, goes here
            if event.eventType == openvr.VREvent_ButtonPress or \
                    event.eventType == openvr.VREvent_ButtonUnpress:
                print(f"event.data.controller.button: {event.data.controller.button}")
                continue
                print(f"event: {dir(event)}")
                print(f"event.data: {dir(event.data)}")
                print(f"event.data.controller: {dir(event.data.controller)}")
                print(f"event.data.controller.button: {event.data.controller.button}")
                print(f"event.data.keyboard: {dir(event.data.keyboard)}")
                print(f"event.data.keyboard.cNewInput: {int.from_bytes(event.data.keyboard.cNewInput, byteorder='little')}")
                print(f"event.data.keyboard.uUserValue: {event.data.keyboard.uUserValue}")
                print(f"event.data.mouse: {dir(event.data.mouse)}")
                print(f"event.data.mouse.button: {event.data.mouse.button}")
                print(f"event.data.touchPadMove: {dir(event.data.touchPadMove)}")
                print(f"event.data.touchPadMove.bFingerDown: {event.data.touchPadMove.bFingerDown}")
                is_rising = event.eventType == openvr.VREvent_ButtonPress
                # Check if the intended button is pressed
                if button == 'thumbstick':
                    _, controller_state = system.getControllerState(event.trackedDeviceIndex)
                    mouse_x = controller_state.rAxis[0].x
                    mouse_y = controller_state.rAxis[0].y
                    print(f"mouse x/y: {mouse_x}/{mouse_y}")
                    print(f"mouse rad: {mouse_x**2 + mouse_y**2}")
                    dead_zone_radius = 0.05
                    thumbstick_moved = mouse_x**2 + mouse_y**2 > dead_zone_radius**2
                    if event.data.controller.button == button_mapping['thumbstick'] and not thumbstick_moved:
                        if is_rising:
                            yield InputEvent(EVENT_RISING_EDGE)
                        else:
                            yield InputEvent(EVENT_FALLING_EDGE)
                elif event.data.controller.button == button_mapping[button]:
                    if is_rising:
                        yield InputEvent(EVENT_RISING_EDGE)
                    else:
                        yield InputEvent(EVENT_FALLING_EDGE)
        # Check poses.
        # TODO(yum) use this. Thinking about adding gestures: swipe to scale
        # up/down, etc.
        if False:
            poses = (openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount)()
            system.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0, poses)
            pose = None
            for i in range(openvr.k_unMaxTrackedDeviceCount):
                if system.getControllerRoleForTrackedDeviceIndex(i) == openvr.TrackedControllerRole_RightHand:
                    pose = poses[i]
            if pose and pose.bPoseIsValid:
                position = pose.mDeviceToAbsoluteTracking.m[0][3], \
                        pose.mDeviceToAbsoluteTracking.m[1][3], \
                        pose.mDeviceToAbsoluteTracking.m[2][3]
                yield InputEvent(EVENT_POSE, pos=position)

        # Max out a 100 Hz.
        time.sleep(0.01)

    openvr.shutdown()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: script_name.py [left|right] [a|b|thumbstick]")
        sys.exit(1)

    hand = sys.argv[1]
    button = sys.argv[2]
    gen = pollButtonPress(hand, button)
    while True:
        print(next(gen))

