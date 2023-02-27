#!/usr/bin/env python3

# The app loop does 2 things:
#   1. Read lines from stdin and send them into the game via OSC.
#   2. Write control info to stdout.
# The app exits when stdin closes.

from playsound import playsound

import argparse
import dataclasses
import generate_utils
import os
import osc_ctrl
import steamvr
import sys
import threading
import time

@dataclasses.dataclass
class AudioState:
    text: str
    osc_state: osc_ctrl.OscState
    enable_local_beep: int
    use_builtin: int
    button: str

    send_transcript: bool
    run_app: bool

def writeControlMessage(run: bool):
    msg = ""
    if run:
        msg += "1"
    else:
        msg += "0"
    print(f"{msg}")

def readControllerInput(audio_state: AudioState):
    session = None
    first = True
    while session == None and audio_state.run_app == True:
        try:
            session = steamvr.SessionState()
        except:
            print("steamvr is off, no controller input", file=sys.stderr)
            session = None
            time.sleep(5)

    RECORD_STATE = 0
    PAUSE_STATE = 1
    state = PAUSE_STATE
    osc_ctrl.indicateSpeech(audio_state.osc_state.client, False)
    osc_ctrl.indicatePaging(audio_state.osc_state.client, False)

    hand_id = steamvr.hands[audio_state.button.split()[0]]
    button_id = steamvr.buttons[audio_state.button.split()[1]]

    last_rising = time.time()
    while audio_state.run_app == True:
        time.sleep(0.05)

        event = steamvr.pollButtonPress(session, hand_id=hand_id,
                button_id=button_id)

        if event == steamvr.EVENT_RISING_EDGE:
            last_rising = time.time()
        elif event == steamvr.EVENT_FALLING_EDGE:
            now = time.time()
            if now - last_rising > 0.3:
                # Long hold
                state = PAUSE_STATE
                if not audio_state.use_builtin:
                    osc_ctrl.indicateSpeech(audio_state.osc_state.client, False)
                    osc_ctrl.toggleBoard(audio_state.osc_state.client, False)

                osc_ctrl.send_transcript = False
                osc_ctrl.clear(audio_state.osc_state)
            else:
                # Short hold
                if state == RECORD_STATE:
                    state = PAUSE_STATE
                    if not audio_state.use_builtin:
                        osc_ctrl.indicateSpeech(audio_state.osc_state.client, False)
                        osc_ctrl.lockWorld(audio_state.osc_state.client, True)

                    osc_ctrl.send_transcript = False

                    if audio_state.enable_local_beep == 1:
                        playsound(os.path.abspath("Resources/Sounds/Noise_Off_Quiet.wav"))
                elif state == PAUSE_STATE:
                    state = RECORD_STATE
                    if not audio_state.use_builtin:
                        osc_ctrl.indicateSpeech(audio_state.osc_state.client, True)
                        osc_ctrl.toggleBoard(audio_state.osc_state.client, True)
                        osc_ctrl.lockWorld(audio_state.osc_state.client, False)

                    osc_ctrl.send_transcript = True
                    osc_ctrl.clear(audio_state.osc_state)

                    audio_state.drop_transcription = True
                    audio_state.audio_paused = False

                    if audio_state.enable_local_beep == 1:
                        playsound(os.path.abspath("Resources/Sounds/Noise_On_Quiet.wav"))

def drainStdin(audio_state: AudioState):
    while True:
        try:
            line = input()
        except EOFError:
            # Invoking process closes the write end of their stdin to signal us
            # to exit.
            # TODO(yum) merge all threads
            audio_state.run_app = False
            return
        if len(line) > 0:
            print(f"stdin get: {line}", file=sys.stderr)

def mainLoop(audio_state: AudioState):
    steamvr_input_thd = threading.Thread(target = readControllerInput,
            args = [audio_state])
    steamvr_input_thd.daemon = True
    steamvr_input_thd.start()

    drain_stdin_thd = threading.Thread(target = drainStdin,
            args = [audio_state])
    drain_stdin_thd.daemon = True
    drain_stdin_thd.start()

    writeControlMessage(False)

    while audio_state.run_app:
        time.sleep(0.01)
        writeControlMessage(audio_state.send_transcript)

if __name__ == "__main__":
    print("args: {}".format(" ".join(sys.argv)), file=sys.stderr)

    # Set cwd to TaSTT/
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    dname = os.path.dirname(dname)
    dname = os.path.dirname(dname)
    os.chdir(dname)
    print(f"Set cwd to {os.getcwd()}", file=sys.stderr)

    parser = argparse.ArgumentParser()
    parser.add_argument("--bytes_per_char", type=str, help="The number of bytes to use to represent each character")
    parser.add_argument("--chars_per_sync", type=str, help="The number of characters to send on each sync event")
    parser.add_argument("--rows", type=int, help="The number of rows on the board")
    parser.add_argument("--cols", type=int, help="The number of columns on the board")
    parser.add_argument("--enable_local_beep", type=int,
            help=("Whether to play a local auditory indicator when "
                "transcription starts/stops."))
    parser.add_argument("--use_builtin", type=int,
            help=("If set to 1, use the text box built into the game."))
    parser.add_argument("--button", type=str,
            help=("The controller button used to start/stop transcription. "
                "E.g. \"left joystick\""))
    args = parser.parse_args()

    if args.bytes_per_char is None or args.chars_per_sync is None:
        print("--bytes_per_char and --chars_per_sync required", file=sys.stderr)
        sys.exit(1)
    if args.rows is None or args.cols is None:
        print("--rows and --cols required", file=sys.stderr)
        sys.exit(1)
    if args.button is None:
        print("--button required", file=sys.stderr)
        sys.exit(1)
    if args.enable_local_beep is None:
        print("--enable_local_beep required", file=sys.stderr)
        sys.exit(1)
    if args.use_builtin is None:
        print("--use_builtin required", file=sys.stderr)
        sys.exit(1)

    generate_utils.config.BYTES_PER_CHAR = int(args.bytes_per_char)
    generate_utils.config.CHARS_PER_SYNC = int(args.chars_per_sync)
    generate_utils.config.BOARD_ROWS = int(args.rows)
    generate_utils.config.BOARD_COLS = int(args.cols)

    audio_state = AudioState(
            text = "",
            osc_state = osc_ctrl.OscState(
                generate_utils.config.CHARS_PER_SYNC,
                generate_utils.config.BOARD_ROWS,
                generate_utils.config.BOARD_COLS),
            button = args.button,
            enable_local_beep = args.enable_local_beep,
            use_builtin = args.use_builtin,
            send_transcript = False,
            run_app = True)

    mainLoop(audio_state)

