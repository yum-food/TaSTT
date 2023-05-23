#!/usr/bin/env python3

from datetime import datetime
from emotes_v2 import EmotesState
from faster_whisper import WhisperModel
from functools import partial
from playsound import playsound

import argparse
import copy
import generate_utils
import keybind_event_machine
import keyboard
import langcodes
import numpy as np
import os
import osc_ctrl
import pyaudio
import steamvr
import string_matcher
import sys
import threading
import time
import wave

class AudioState:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        # This matches the framerate expected by whisper.
        self.RATE = 16000

        # The maximum length that recordAudio() will put into frames before it
        # starts dropping from the start.
        self.MAX_LENGTH_S = 30
        # The minimum length that recordAudio() will wait for before saving audio.
        self.MIN_LENGTH_S = 1

        # PyAudio object
        self.p = None

        # PyAudio stream object
        self.stream = None

        self.text = ""
        self.committed_text = ""
        self.frames = []

        # Locks access to `text`.
        self.transcribe_lock = threading.Lock()

        # Locks access to `frames`, and audio stored on disk.
        self.audio_lock = threading.Lock()

        # Used to tell the threads when to stop.
        self.run_app = True

        self.transcribe_sleep_duration_min_s = 0.05
        self.transcribe_sleep_duration_max_s = 5.00
        self.transcribe_no_change_count = 0
        self.transcribe_sleep_duration = self.transcribe_sleep_duration_min_s

        # The transcription thread transcribes without holding locks, then
        # blocks on it. Thus we need some way to tell the transcription
        # thread to drop that transcription.
        self.drop_transcription = False

        # The language the user is speaking in. Default is English but user may set
        # this to whatever they want.
        self.language = "en"

        self.audio_paused = False

        self.osc_state = osc_ctrl.OscState(generate_utils.config.CHARS_PER_SYNC,
                generate_utils.config.BOARD_ROWS,
                generate_utils.config.BOARD_COLS)

    def sleepInterruptible(self, dur_s, stride_ms = 5):
        dur_ms = dur_s * 1000.0
        timeout = time.time() + dur_s
        while self.audio_paused and self.run_app and time.time() < timeout:
            time.sleep(stride_ms / 1000.0)

def dumpMicDevices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            device_name = p.get_device_info_by_host_api_device_index(0, i).get('name')
            print("Input Device id ", i, " - ", device_name)

def onAudioFramesAvailable(
        audio_state,
        input_rate,
        frames,
        frame_count,
        time_info,
        status_flags):
    if audio_state.audio_paused:
        return (frames, pyaudio.paContinue)

    # Reduce sample rate from mic rate to Whisper rate by dropping frames.
    decimated = b''
    frame_len = int(len(frames) / frame_count)
    next_frame = 0.0
    keep_every = float(input_rate) / audio_state.RATE
    i = 0
    for i in range(0, frame_count):
        if i >= next_frame:
            decimated += frames[i*frame_len:(i+1)*frame_len]
            next_frame += keep_every
        i += 1

    audio_state.frames.append(decimated)

    max_frames = int(input_rate * audio_state.MAX_LENGTH_S /
            audio_state.CHUNK)
    if len(audio_state.frames) > max_frames:
        audio_state.frames = audio_state.frames[-1 * max_frames:]


    return (frames, pyaudio.paContinue)

def getMicStream(which_mic):
    audio_state = AudioState()
    audio_state.p = pyaudio.PyAudio()

    print("Finding mic {}...".format(which_mic))
    dumpMicDevices()
    got_match = False
    device_index = -1
    focusrite_str = "Focusrite"
    index_str = "Digital Audio Interface"
    if which_mic == "index":
        target_str = index_str
    elif which_mic == "focusrite":
        target_str = focusrite_str
    else:
        print("Mic {} requested, treating it as a numerical device ID".format(which_mic))
        device_index = int(which_mic)
        got_match = True

    while got_match == False:
        info = audio_state.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (audio_state.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                device_name = audio_state.p.get_device_info_by_host_api_device_index(0, i).get('name')
                if target_str in device_name:
                    print("Got match: {}".format(device_name))
                    device_index = i
                    got_match = True
                    break
        if got_match == False:
            print("No match, sleeping")
            time.sleep(3)

    info = audio_state.p.get_device_info_by_host_api_device_index(0, device_index)
    input_rate = int(info['defaultSampleRate'])
    print("input rate: {}".format(input_rate))

    # Bind audio_state to onAudioFramesAvailable
    callback = partial(onAudioFramesAvailable, audio_state, input_rate)

    audio_state.stream = audio_state.p.open(
            rate=input_rate,
            channels=audio_state.CHANNELS,
            format=audio_state.FORMAT,
            input=True, frames_per_buffer=audio_state.CHUNK,
            input_device_index=device_index,
            stream_callback=callback)

    audio_state.stream.start_stream()

    return audio_state

def resetAudioLocked(audio_state):
    audio_state.frames = []
    audio_state.transcribe_no_change_count = 0
    audio_state.transcribe_sleep_duration = \
            audio_state.transcribe_sleep_duration_min_s

    audio_state.committed_text = ""
    audio_state.text = ""

def resetDisplayLocked(audio_state):
    osc_ctrl.clear(audio_state.osc_state)

def resetAudio(audio_state):
    audio_state.transcribe_lock.acquire()
    audio_state.audio_lock.acquire()
    resetAudioLocked(audio_state)
    audio_state.audio_lock.release()
    audio_state.transcribe_lock.release()

# Transcribe the audio recorded in a file.
def transcribe(audio_state, model, frames, use_cpu: bool):
    start_time = time.time()

    frames = audio_state.frames
    # Convert from signed 16-bit int [-32768, 32767] to signed 16-bit float on
    # [-1, 1].
    # We should technically acquire a lock to protect frames, but this is
    # really slow and in practice it doesn't make the app crash, so who cares.
    frames = np.asarray(audio_state.frames)
    audio = np.frombuffer(frames, np.int16).flatten().astype(np.float32) / 32768.0

    segments, info = model.transcribe(
            audio,
            beam_size = 5,
            language = audio_state.language,
            vad_filter = True,
            without_timestamps = True)

    return "".join(s.text for s in segments)

def transcribeAudio(audio_state, model, use_cpu: bool):
    last_transcribe_time = time.time()
    while audio_state.run_app == True:
        # Pace this out
        if audio_state.audio_paused:
            audio_state.sleepInterruptible(audio_state.transcribe_sleep_duration)
        else:
            time.sleep(0.05)

        audio_state.transcribe_no_change_count += 1
        # Increase sleep time. Code below will set sleep time back to minimum
        # if a change is detected.
        longer_sleep_dur = audio_state.transcribe_sleep_duration
        longer_sleep_dur += audio_state.transcribe_sleep_duration_min_s * (1.3**audio_state.transcribe_no_change_count)
        if audio_state.audio_paused:
            audio_state.transcribe_sleep_duration = min(
                    1000 * 1000,
                    longer_sleep_dur)
        else:
            audio_state.transcribe_sleep_duration = min(
                    audio_state.transcribe_sleep_duration_max_s,
                    longer_sleep_dur)

        text = transcribe(audio_state, model, audio_state.frames, use_cpu)
        if not text:
            print("no transcription, spin ({} seconds)".format(time.time() - last_transcribe_time))
            last_transcribe_time = time.time()
            continue

        if audio_state.drop_transcription:
            audio_state.drop_transcription = False
            print("drop transcription ({} seconds)".format(time.time() - last_transcribe_time))
            last_transcribe_time = time.time()
            continue

        old_text = audio_state.text
        audio_state.text = string_matcher.matchStrings(audio_state.text,
                text, window_size = 25)

        now = time.time()
        print("Transcription ({} seconds): {}".format(
            now - last_transcribe_time,
            audio_state.text))
        last_transcribe_time = now

        if old_text != audio_state.text:
            # We think the user said something, so  reset the amount of
            # time we sleep between transcriptions to the minimum.
            audio_state.transcribe_no_change_count = 0
            audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s

def sendAudio(audio_state, use_builtin: bool, estate: EmotesState):
    while audio_state.run_app == True:
        text = audio_state.committed_text + " " + audio_state.text
        if use_builtin:
            ret = osc_ctrl.pageMessageBuiltin(audio_state.osc_state, text)
            time.sleep(1.5)
        else:
            ret = osc_ctrl.pageMessage(audio_state.osc_state, text, estate)
            is_paging = (ret == False)
            osc_ctrl.indicatePaging(audio_state.osc_state.client, is_paging)

            # Pace this out
            time.sleep(0.01)

def readKeyboardInput(audio_state, enable_local_beep: bool,
        use_builtin: bool, keybind: str):
    machine = keybind_event_machine.KeybindEventMachine(keybind)
    last_press_time = 0

    # double pressing the keybind
    double_press_timeout = 0.25

    RECORD_STATE = 0
    PAUSE_STATE = 1
    state = PAUSE_STATE

    while audio_state.run_app == True:
        time.sleep(0.05)

        cur_press_time = machine.getNextPressTime()
        if cur_press_time == 0:
            continue

        EVENT_SINGLE_PRESS = 0
        EVENT_DOUBLE_PRESS = 1
        if last_press_time == 0:
            event = EVENT_SINGLE_PRESS
        elif cur_press_time - last_press_time < double_press_timeout:
            event = EVENT_DOUBLE_PRESS
        else:
            event = EVENT_SINGLE_PRESS
        last_press_time = cur_press_time

        if event == EVENT_DOUBLE_PRESS:
            state = PAUSE_STATE
            if not use_builtin:
                osc_ctrl.indicateSpeech(audio_state.osc_state.client, False)
                osc_ctrl.toggleBoard(audio_state.osc_state.client, False)
            #playsound(os.path.abspath("../Sounds/Noise_Off_Quiet.wav"))

            resetAudioLocked(audio_state)
            resetDisplayLocked(audio_state)
            audio_state.drop_transcription = True
            audio_state.audio_paused = True
            continue

        # Short hold
        if state == RECORD_STATE:
            state = PAUSE_STATE
            if not use_builtin:
                osc_ctrl.indicateSpeech(audio_state.osc_state.client, False)
                osc_ctrl.lockWorld(audio_state.osc_state.client, True)
            audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s

            audio_state.audio_paused = True

            if enable_local_beep == 1:
                playsound(os.path.abspath("Resources/Sounds/Noise_Off_Quiet.wav"),
                    block=False)
        elif state == PAUSE_STATE:
            state = RECORD_STATE
            if not use_builtin:
                osc_ctrl.indicateSpeech(audio_state.osc_state.client, True)
                osc_ctrl.toggleBoard(audio_state.osc_state.client, True)
                osc_ctrl.lockWorld(audio_state.osc_state.client, False)
            resetAudioLocked(audio_state)
            resetDisplayLocked(audio_state)

            audio_state.drop_transcription = True
            audio_state.audio_paused = False

            if enable_local_beep == 1:
                playsound(os.path.abspath("Resources/Sounds/Noise_On_Quiet.wav"),
                    block=False)

def readControllerInput(audio_state, enable_local_beep: bool,
        use_builtin: bool, button: str):
    session = None
    first = True
    while session == None and audio_state.run_app == True:
        try:
            session = steamvr.SessionState()
        except:
            print("steamvr is off, no controller input")
            session = None
            time.sleep(5)

    RECORD_STATE = 0
    PAUSE_STATE = 1
    state = PAUSE_STATE
    osc_ctrl.indicateSpeech(audio_state.osc_state.client, False)
    osc_ctrl.indicatePaging(audio_state.osc_state.client, False)

    hand_id = steamvr.hands[button.split()[0]]
    button_id = steamvr.buttons[button.split()[1]]

    # Rough description of state machine:
    #   Single short press: toggle transcription
    #   Medium press: dismiss custom chatbox
    #   Long press: update chatbox in place
    #   Medium press + long press: type transcription

    last_rising = time.time()
    last_medium_press_end = 0
    while audio_state.run_app == True:
        time.sleep(0.05)

        event = steamvr.pollButtonPress(session, hand_id=hand_id,
                button_id=button_id)

        if event == steamvr.EVENT_RISING_EDGE:
            last_rising = time.time()

            if state == PAUSE_STATE:
                resetAudioLocked(audio_state)
                resetDisplayLocked(audio_state)
                audio_state.drop_transcription = True
                audio_state.audio_paused = False

        elif event == steamvr.EVENT_FALLING_EDGE:
            now = time.time()
            if now - last_rising > 1.5:
                # Long press: treat as the end of transcription.
                state = PAUSE_STATE
                if not use_builtin:
                    osc_ctrl.indicateSpeech(audio_state.osc_state.client, False)
                    osc_ctrl.lockWorld(audio_state.osc_state.client, True)
                audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s
                audio_state.audio_paused = True

                if last_rising - last_medium_press_end < 1.0:
                    # Type transcription
                    if enable_local_beep == 1:
                        playsound(os.path.abspath("Resources/Sounds/KB_Noise_Off_Quiet.wav"),
                            block=False)
                    keyboard.write(audio_state.text)
                else:
                    if enable_local_beep == 1:
                        playsound(os.path.abspath("Resources/Sounds/Noise_Off_Quiet.wav"),
                            block=False)

            elif now - last_rising > 0.5:
                # Medium press
                last_medium_press_end = now
                state = PAUSE_STATE

                if enable_local_beep == 1:
                    playsound(os.path.abspath("Resources/Sounds/Dismiss_Noise_Quiet.wav"),
                        block=False)

                if not use_builtin:
                    osc_ctrl.indicateSpeech(audio_state.osc_state.client, False)
                    osc_ctrl.toggleBoard(audio_state.osc_state.client, False)

                resetAudioLocked(audio_state)
                resetDisplayLocked(audio_state)
                audio_state.drop_transcription = True
                audio_state.audio_paused = True
            else:
                # Short hold
                if state == RECORD_STATE:
                    state = PAUSE_STATE
                    if not use_builtin:
                        osc_ctrl.indicateSpeech(audio_state.osc_state.client, False)
                        osc_ctrl.lockWorld(audio_state.osc_state.client, True)
                    audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s

                    audio_state.audio_paused = True

                    if enable_local_beep == 1:
                        playsound(os.path.abspath("Resources/Sounds/Noise_Off_Quiet.wav"),
                            block=False)
                elif state == PAUSE_STATE:
                    state = RECORD_STATE

                    if enable_local_beep == 1:
                        playsound(os.path.abspath("Resources/Sounds/Noise_On_Quiet.wav"),
                            block=False)

                    if not use_builtin:
                        osc_ctrl.indicateSpeech(audio_state.osc_state.client, True)
                        osc_ctrl.toggleBoard(audio_state.osc_state.client, True)
                        osc_ctrl.lockWorld(audio_state.osc_state.client, False)

# model should correspond to one of the Whisper models defined in
# whisper/__init__.py. Examples: tiny, base, small, medium.
def transcribeLoop(mic: str, language: str, model: str,
        enable_local_beep: bool, use_cpu: bool, use_builtin: bool,
        button: str, estate: EmotesState,
        window_duration_s: int, gpu_idx: int,
        keyboard_hotkey: str):
    audio_state = getMicStream(mic)
    audio_state.language = langcodes.find(language).language
    audio_state.MAX_LENGTH_S = window_duration_s

    print("Safe to start talking")

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    model_root = os.path.join(dname, "Models", model)

    print("Model {} will be saved to {}".format(model, model_root))

    model_device = "cuda"
    if use_cpu:
        model_device = "cpu"

    download_it = os.path.exists(model_root)
    if download_it:
        model = model_root
    model = WhisperModel(model,
            device = model_device,
            compute_type = "int8",
            download_root = model_root,
            local_files_only = download_it)

    transcribe_audio_thd = threading.Thread(target = transcribeAudio, args = [audio_state, model, use_cpu])
    transcribe_audio_thd.daemon = True
    transcribe_audio_thd.start()

    send_audio_thd = threading.Thread(target = sendAudio, args = [audio_state, use_builtin, estate])
    send_audio_thd.daemon = True
    send_audio_thd.start()

    controller_input_thd = threading.Thread(target = readControllerInput, args
            = [audio_state, enable_local_beep, use_builtin, button])
    controller_input_thd.daemon = True
    controller_input_thd.start()

    keyboard_input_thd = threading.Thread(target = readKeyboardInput, args
            = [audio_state, enable_local_beep, use_builtin, keyboard_hotkey])
    keyboard_input_thd.daemon = True
    keyboard_input_thd.start()

    print("Press enter to start a new message.")
    for line in sys.stdin:
        audio_state.transcribe_lock.acquire()
        audio_state.audio_lock.acquire()
        resetAudioLocked(audio_state)
        resetDisplayLocked(audio_state)
        audio_state.drop_transcription = True
        audio_state.audio_paused = False
        audio_state.audio_lock.release()
        audio_state.transcribe_lock.release()
        if "exit" in line or "quit" in line:
            break

    print("Joining threads")
    audio_state.run_app = False
    transcribe_audio_thd.join()
    controller_input_thd.join()
    keyboard_input_thd.join()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    print("args: {}".format(" ".join(sys.argv)))

    # Set cwd to TaSTT/
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    dname = os.path.dirname(dname)
    dname = os.path.dirname(dname)
    #os.chdir(dname)
    print(f"Set cwd to {os.getcwd()}")

    parser = argparse.ArgumentParser()
    parser.add_argument("--mic", type=str, help="Which mic to use. Options: index, focusrite. Default: index")
    parser.add_argument("--language", type=str, help="Which language to use. Ex: english, japanese, chinese, french, german.")
    parser.add_argument("--model", type=str, help="Which AI model to use. \
            Options: tiny, tiny.en, base, base.en, small, small.en, \
            medium, medium.en, large-v1, large-v2")
    parser.add_argument("--bytes_per_char", type=str, help="The number of bytes to use to represent each character")
    parser.add_argument("--chars_per_sync", type=str, help="The number of characters to send on each sync event")
    parser.add_argument("--enable_local_beep", type=int, help="Whether to play a local auditory indicator when transcription starts/stops.")
    parser.add_argument("--rows", type=int, help="The number of rows on the board")
    parser.add_argument("--cols", type=int, help="The number of columns on the board")
    parser.add_argument("--window_duration_s", type=int, help="The length in seconds of the audio recording handed to the transcription algorithm")
    parser.add_argument("--cpu", type=int, help="If set to 1, use CPU instead of GPU")
    parser.add_argument("--use_builtin", type=int, help="If set to 1, use the text box built into the game.")
    parser.add_argument("--button", type=str, help="The controller button used to start/stop transcription. E.g. \"left joystick\"")
    parser.add_argument("--emotes_pickle", type=str, help="The path to emotes pickle. See emotes_v2.py for details.")
    parser.add_argument("--gpu_idx", type=str, help="The index of the GPU device to use. On single GPU systems, use 0.")
    parser.add_argument("--keybind", type=str, help="The keyboard hotkey to use to toggle transcription. For example, ctrl+shift+s")
    args = parser.parse_args()

    if not args.mic:
        args.mic = "index"

    if not args.language:
        args.language = "english"

    if not args.model:
        args.model = "base"

    if not args.bytes_per_char or not args.chars_per_sync:
        print("--bytes_per_char and --chars_per_sync required", file=sys.stderr)
        sys.exit(1)

    if not args.rows or not args.cols:
        print("--rows and --cols required", file=sys.stderr)
        sys.exit(1)

    if not args.button:
        print("--button required", file=sys.stderr)
        sys.exit(1)

    if not args.emotes_pickle:
        print("--emotes_pickle required", file=sys.stderr)
        sys.exit(1)

    if not args.gpu_idx:
        print("--gpu_idx required", file=sys.stderr)
        sys.exit(1)
    args.gpu_idx = int(args.gpu_idx)

    window_duration_s = 120
    if args.window_duration_s:
        window_duration_s = int(args.window_duration_s)

    if args.cpu == 1:
        args.cpu = True
    else:
        args.cpu = False

    if args.use_builtin == 1:
        args.use_builtin = True
    else:
        args.use_builtin = False

    estate = EmotesState()
    estate.load(args.emotes_pickle)

    generate_utils.config.BYTES_PER_CHAR = int(args.bytes_per_char)
    generate_utils.config.CHARS_PER_SYNC = int(args.chars_per_sync)
    generate_utils.config.BOARD_ROWS = int(args.rows)
    generate_utils.config.BOARD_COLS = int(args.cols)

    print(f"PATH: {os.environ['PATH']}")

    transcribeLoop(args.mic, args.language, args.model, args.enable_local_beep,
            args.cpu, args.use_builtin, args.button, estate, window_duration_s,
            args.gpu_idx, args.keybind)

