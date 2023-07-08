#!/usr/bin/env python3

from datetime import datetime
from emotes_v2 import EmotesState
from faster_whisper import WhisperModel
from functools import partial
from math import ceil, floor
from playsound import playsound
from profanity_filter import ProfanityFilter
from sentence_splitter import split_text_into_sentences

import argparse
import copy
import ctranslate2
import editdistance
import generate_utils
import keybind_event_machine
import keyboard
import lang_compat
import langcodes
import numpy as np
import os
import osc_ctrl
import pyaudio
import steamvr
import subprocess
import sys
import threading
import time
import transformers
import typing
import wave

class AudioState:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        # This matches the framerate expected by whisper.
        self.RATE = 16000

        # If set, print additional information to stdout while transcribing.
        self.enable_debug_mode = False

        # The maximum length that recordAudio() will put into frames before it
        # starts dropping from the start.
        self.MAX_LENGTH_S = 300
        # The minimum length that recordAudio() will wait for before saving audio.
        self.MIN_LENGTH_S = 1

        # PyAudio object
        self.p = None

        # PyAudio stream object
        self.stream = None

        self.preview_text = ""
        self.text = ""
        self.filtered_text = ""

        # If set to true, then the transcript strings (`text` and friends) will
        # be reset whenever transcription is toggled on. At time of writing,
        # this only applies to keyboard controls.
        self.reset_on_toggle = True

        # The edit distance under which two consecutive transcripts are
        # considered to match. This affects how easily `preview_text`
        # gets appended to `text`.
        self.commit_fuzz_threshold = 8

        # If set, profanity in transcriptions will have their vowels replaced
        # with asterisks. Only works in English.
        self.enable_profanity_filter = False
        self.profanity_filter: ProfanityFilter = None

        # List of:
        #   List of tuples of:
        #     Segment start time, end time, and text
        self.ranges_ls = []
        self.frames = []
        self.drop_samples_till_i = -1

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
        self.language = "english"

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
    # Reduce sample rate from mic rate to Whisper rate by dropping frames.
    decimated = b''
    frame_len = int(len(frames) / frame_count)
    next_frame = 0.0
    keep_every = float(input_rate) / audio_state.RATE
    #print(f"Keep every {keep_every}th frame")
    #print(f"len frames: {len(frames)}")
    #print(f"len decimated: {len(decimated)}")
    i = 0
    for i in range(0, frame_count):
        if i >= next_frame:
            decimated += frames[i*frame_len:(i+1)*frame_len]
            next_frame += keep_every
        i += 1

    if not audio_state.audio_paused:
        audio_state.frames.append(decimated)

    max_frames = int(input_rate * audio_state.MAX_LENGTH_S /
            audio_state.CHUNK)
    if len(audio_state.frames) > max_frames:
        audio_state.frames = audio_state.frames[-1 * max_frames:]
    if audio_state.drop_samples_till_i > 0:
        # Caller wants us to keep this many *whisper* samples, assuming that
        # we're getting one full frame every (1024 / 16KHz) seconds.
        # However we really get one full whisper frame a little slower, since
        # mics usually have a higher sample rate than 16 KHz (see decimation
        # code above).
        # The ratio of (mic sample rate) / (16KHz) is simply `keep_every`.
        n_frames_to_drop = audio_state.drop_samples_till_i / audio_state.CHUNK
        n_frames_to_drop *= keep_every
        n_frames_to_drop = int(floor(n_frames_to_drop))
        if audio_state.enable_debug_mode:
            print(f"Dropping {n_frames_to_drop} frames, buffer has {len(audio_state.frames)} frames total")
        # First drop every whole chunk
        audio_state.frames = audio_state.frames[n_frames_to_drop:]
        # Then drop the part of the most recent chunk we no longer want
        if len(audio_state.frames) > 0:
            n_samples_to_drop = int(ceil((n_frames_to_drop % 1.0) * audio_state.CHUNK))
            bytes_per_sample = 2
            audio_state.frames[0] = audio_state.frames[0][n_samples_to_drop * bytes_per_sample:]
        audio_state.drop_samples_till_i = -1

    # Now enforce a minimum duration on frames. This reduces cases where the
    # STT hallucinates random things. In the Whisper paper, they enforce a
    # minimum audio buffer duration of 5.0 seconds, so I do the same here.
    empty_chunk = b'00' * int(ceil(audio_state.CHUNK / keep_every))
    chunk_duration_s = float(audio_state.CHUNK) / audio_state.RATE
    cur_duration_s = len(audio_state.frames) * chunk_duration_s
    desired_min_duration_s = 5.0
    delta_duration_s = desired_min_duration_s - cur_duration_s
    if delta_duration_s > 0:
        delta_chunks = int(ceil(delta_duration_s / chunk_duration_s))
        if audio_state.enable_debug_mode:
            print(f"Padding with {delta_duration_s} seconds ({delta_chunks} chunks) of silence")
            print(f"Each chunk has {len(empty_chunk)} samples")
        audio_state.frames = [empty_chunk] * delta_chunks + audio_state.frames

    return (frames, pyaudio.paContinue)

def getMicStream(which_mic) -> AudioState:
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

    if audio_state.reset_on_toggle:
        if audio_state.enable_debug_mode:
            print("resetAudioLocked resetting text")
        audio_state.text = ""
        audio_state.preview_text = ""
        audio_state.filtered_text = ""

def resetDisplayLocked(audio_state):
    osc_ctrl.clear(audio_state.osc_state)

# Transcribe the audio recorded in a file.
# Returns two strings: committed text, and preview text.
# Committed text is temporally stable. Preview text is *not* temporally stable,
# but is lower latency than committed text.
def transcribe(audio_state, model, frames, use_cpu: bool) -> typing.Tuple[str,str]:
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
            temperature = 0.0,
            log_prob_threshold = -0.8,
            vad_filter = True,
            condition_on_previous_text = True,
            without_timestamps = False)
    ranges = []
    for s in segments:
        if s.avg_logprob < -0.8 or s.no_speech_prob > 0.6:
            continue
        if audio_state.enable_debug_mode:
            print(f"Segment: {s}")
        ranges.append((s.start, s.end, s.text))
    audio_state.ranges_ls.append(ranges)

    committed_text = ""
    if True:
        # Tuple of (start time, end time, transcript)
        first_segments = []
        for ranges in audio_state.ranges_ls:
            for segment in ranges:
                first_segments.append(segment)
                break
        if len(first_segments) >= 4:
            # Hack: require convergence across many frames to give the
            # algorithm a longer buffer to work with.
            c0 = first_segments[-1]
            c1 = first_segments[-2]
            c2 = first_segments[-3]
            c3 = first_segments[-4]

            c0_c1_d = editdistance.eval(c0[2], c1[2])
            c1_c2_d = editdistance.eval(c1[2], c2[2])
            c2_c3_d = editdistance.eval(c2[2], c3[2])

            max_edit = audio_state.commit_fuzz_threshold

            if audio_state.enable_debug_mode:
                print(f"c0: {c0}, c1: {c1}, c2: {c2}, c3: {c3}")
            if c0_c1_d < max_edit and c1_c2_d < max_edit and c2_c3_d < max_edit:
                # For simplicity, completely reset saved audio ranges.
                audio_state.ranges_ls = []
                committed_text = c0[2]
                if audio_state.enable_debug_mode:
                    print(f"Dropping frames until {c0[1]}")
                n_samples_to_drop = int(ceil(audio_state.RATE * c0[1]))
                audio_state.drop_samples_till_i = n_samples_to_drop

    preview_text = ""
    for seg in ranges:
        if seg[2] == committed_text:
            continue
        preview_text += seg[2]

    return (committed_text, preview_text)

def transcribeAudio(audio_state,
        model,
        use_cpu: bool,
        enable_uwu_filter: bool,
        remove_trailing_period: bool,
        enable_uppercase_filter: bool,
        enable_lowercase_filter: bool,
        ):
    print("Ready!")
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

        text, preview_text = transcribe(audio_state, model, audio_state.frames, use_cpu)
        if len(text) == 0 and len(preview_text) == 0:
            if audio_state.enable_debug_mode:
                print("no transcription, spin ({} seconds)".format(time.time() - last_transcribe_time))
            last_transcribe_time = time.time()
            continue

        if audio_state.drop_transcription:
            audio_state.drop_transcription = False
            audio_state.text = ""
            audio_state.preview_text = ""
            audio_state.filtered_text = ""
            if audio_state.enable_debug_mode:
                print("drop transcription ({} seconds)".format(time.time() - last_transcribe_time))
            last_transcribe_time = time.time()
            continue

        old_text = audio_state.text
        audio_state.text += text
        audio_state.preview_text = audio_state.text + preview_text

        if len(preview_text) == 0:
            print("Finalized: 1")
        else:
            print("Finalized: 0")

        # Hard cap transcript at 4096 chars. Letting it grow longer than this
        # eventually causes lag. This happens routinely when streaming. Capping
        # like this does not affect the visible portion of the transcript in
        # OBS, but it might affect the visible portion in-game. (Don't make
        # your friends read more than 4k characters on a fucking chatbox.)
        audio_state.text = audio_state.text[-4096:]

        now = time.time()
        if audio_state.enable_debug_mode:
            print("Raw transcription ({} seconds): {}".format(
                now - last_transcribe_time,
                audio_state.preview_text))
            last_transcribe_time = now
            print(f"Commit text: {text}")
            print(f"Preview text: {preview_text}")

        # Translate if requested.
        translated = audio_state.preview_text
        if audio_state.language_target:
            whisper_lang = audio_state.whisper_language
            nllb_lang = lang_compat.whisper_to_nllb[whisper_lang]
            ss_lang = lang_compat.nllb_to_ss[nllb_lang]
            sentences = split_text_into_sentences(translated, language=ss_lang)

            translated_sentences = []
            for sentence in sentences:
                source = audio_state.tokenizer.convert_ids_to_tokens(audio_state.tokenizer.encode(sentence))
                target_prefix = [audio_state.language_target]
                results = audio_state.translator.translate_batch([source], target_prefix=[target_prefix])
                target = results[0].hypotheses[0][1:]
                translated_sentence = audio_state.tokenizer.decode(audio_state.tokenizer.convert_tokens_to_ids(target))
                translated_sentences.append(translated_sentence)
            translated = " ".join(translated_sentences)
            print(f"Translation: {translated}")

        # Apply filters to transcription
        filtered_text = translated
        if enable_uwu_filter:
            uwu_proc = subprocess.Popen(["Resources/Uwu/Uwwwu.exe", filtered_text],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            uwu_stdout, uwu_stderr = uwu_proc.communicate()
            uwu_text = uwu_stdout.decode("utf-8")
            uwu_text = uwu_text.replace("\n", "")
            uwu_text = uwu_text.replace("\r", "")
            filtered_text = uwu_text
        if remove_trailing_period:
            if len(filtered_text) > 0 and filtered_text[-1] == '.' and not filtered_text.endswith("..."):
                filtered_text = filtered_text[0:len(filtered_text)-1]
        if enable_uppercase_filter:
            filtered_text = filtered_text.upper()
        if enable_lowercase_filter:
            filtered_text = filtered_text.lower()
        if audio_state.enable_profanity_filter:
            filtered_text = audio_state.profanity_filter.filter(filtered_text)
        audio_state.filtered_text = filtered_text

        now = time.time()
        print("Transcription ({} seconds): {}".format(
            now - last_transcribe_time,
            filtered_text))
        last_transcribe_time = now

        if old_text != audio_state.preview_text:
            # We think the user said something, so  reset the amount of
            # time we sleep between transcriptions to the minimum.
            audio_state.transcribe_no_change_count = 0
            audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s

def sendAudio(audio_state, use_builtin: bool, estate: EmotesState):
    while audio_state.run_app == True:
        text = audio_state.filtered_text
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
    double_press_timeout = 0.5

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

            if audio_state.reset_on_toggle:
                if audio_state.enable_debug_mode:
                    print("Toggle detected, dropping transcript (1)")
                audio_state.drop_transcription = True
            else:
                if audio_state.enable_debug_mode:
                    print("Toggle detected, committing preview text (1)")
                audio_state.text += audio_state.preview_text
            audio_state.audio_paused = True
            resetAudioLocked(audio_state)
            resetDisplayLocked(audio_state)
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
            if audio_state.reset_on_toggle:
                if audio_state.enable_debug_mode:
                    print("Toggle detected, dropping transcript (2)")
                audio_state.drop_transcription = True
            else:
                if audio_state.enable_debug_mode:
                    print("Toggle detected, committing preview text (2)")
                audio_state.text += audio_state.preview_text
            audio_state.audio_paused = False

            resetAudioLocked(audio_state)
            resetDisplayLocked(audio_state)

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
            if audio_state.enable_debug_mode:
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
                    keyboard.write(audio_state.filtered_text)
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
                    if not use_builtin:
                        osc_ctrl.indicateSpeech(audio_state.osc_state.client, True)
                        osc_ctrl.toggleBoard(audio_state.osc_state.client, True)
                        osc_ctrl.lockWorld(audio_state.osc_state.client, False)
                    if audio_state.reset_on_toggle:
                        if audio_state.enable_debug_mode:
                            print("Toggle detected, dropping transcript (3)")
                        audio_state.drop_transcription = True
                    else:
                        if audio_state.enable_debug_mode:
                            print("Toggle detected, committing preview text (3)")
                        audio_state.text += audio_state.preview_text

                    resetAudioLocked(audio_state)
                    resetDisplayLocked(audio_state)

                    if enable_local_beep == 1:
                        playsound(os.path.abspath("Resources/Sounds/Noise_On_Quiet.wav"),
                            block=False)

# model should correspond to one of the Whisper models defined in
# whisper/__init__.py. Examples: tiny, base, small, medium.
def transcribeLoop(mic: str,
        language: str,
        language_target: str,
        model: str,
        model_translation: str,
        enable_local_beep: bool,
        use_cpu: bool,
        use_builtin: bool,
        enable_uwu_filter: bool,
        remove_trailing_period: bool,
        enable_uppercase_filter: bool,
        enable_lowercase_filter: bool,
        enable_profanity_filter: bool,
        enable_debug_mode: bool,
        button: str,
        estate: EmotesState,
        window_duration_s: int,
        gpu_idx: int,
        keyboard_hotkey: str,
        reset_on_toggle: bool,
        commit_fuzz_threshold: int):
    audio_state = getMicStream(mic)
    audio_state.whisper_language = language
    audio_state.language = langcodes.find(language).language
    audio_state.MAX_LENGTH_S = window_duration_s
    audio_state.reset_on_toggle = reset_on_toggle
    audio_state.commit_fuzz_threshold = commit_fuzz_threshold
    audio_state.enable_debug_mode = enable_debug_mode
    audio_state.enable_profanity_filter = enable_profanity_filter

    # Set up profanity filter
    en_profanity_path = os.path.abspath("Resources/Profanity/en")
    audio_state.profanity_filter = ProfanityFilter(en_profanity_path)
    if enable_profanity_filter:
        audio_state.profanity_filter.load()

    lang_bits = language_target.split(" | ")
    if len(lang_bits) == 2:
        lang_code = lang_bits[1]
        audio_state.language_target = lang_code
    else:
        audio_state.language_target = None

    if audio_state.language_target:
        print("Translation requested")

        print("Installing torch and sentencepiece in virtual environment. "
                "Nothing will print "
                "for several minutes while these download (~2.4 GB).")
        pip_proc = subprocess.Popen(
                "Resources/Python/python.exe -m pip install sentencepiece torch".split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        pip_stdout, pip_stderr = pip_proc.communicate()
        pip_stdout = pip_stdout.decode("utf-8")
        pip_stderr = pip_stderr.decode("utf-8")
        print(pip_stdout)
        print(pip_stderr)
        if pip_proc.returncode != 0:
            print(f"Failed to set up for translation: `pip install torch` "
                    "exited with {pip_proc.returncode}")

        output_dir = "Resources/" + model_translation
        # Provided by ctranslate2 Python package
        cmd = "ct2-transformers-converter.exe --model facebook/" + model_translation + " --output_dir " + output_dir

        print(f"Fetching translation algorithm ({model_translation})")
        if not os.path.exists(output_dir):
            ct2_proc = subprocess.Popen(
                    cmd.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            ct2_stdout, ct2_stderr = ct2_proc.communicate()
            ct2_stdout = ct2_stdout.decode("utf-8")
            ct2_stderr = ct2_stderr.decode("utf-8")
            print(ct2_stdout)
            print(ct2_stderr)
            if ct2_proc.returncode != 0:
                print(f"Failed to get NLLB model: ct2 process exited with "
                        "{ct2_proc.returncode}")
        print(f"Using model at {output_dir}")

        audio_state.translator = ctranslate2.Translator(output_dir)

        whisper_lang = audio_state.whisper_language
        nllb_lang = lang_compat.whisper_to_nllb[whisper_lang]

        audio_state.tokenizer = transformers.AutoTokenizer.from_pretrained(
                "facebook/" + model_translation,
                src_lang=nllb_lang)

        print(f"Translation ready to go")

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
            device_index = gpu_idx,
            compute_type = "int8",
            download_root = model_root,
            local_files_only = download_it)

    transcribe_audio_thd = threading.Thread(
            target = transcribeAudio,
            args = [audio_state, model, use_cpu, enable_uwu_filter,
                remove_trailing_period, enable_uppercase_filter,
                enable_lowercase_filter])
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

    print(f"Set cwd to {os.getcwd()}")

    parser = argparse.ArgumentParser()
    parser.add_argument("--mic", type=str, help="Which mic to use. Options: index, focusrite. Default: index")
    parser.add_argument("--language", type=str, help="Which language to use. Ex: english, japanese, chinese, french, german.")
    parser.add_argument("--language_target", type=str, help="Which language to translate into. See kLangTargetChoices in Frame.cpp for valid choices")
    parser.add_argument("--model", type=str, help="Which transcription model to use. " \
            "Options: tiny, tiny.en, base, base.en, small, small.en, " \
            "medium, medium.en, large-v1, large-v2")
    parser.add_argument("--model_translation", type=str, help="Which translation model to use. " \
            "Options: nllb-200-distilled-600M, nllb-200-distilled-1.3B.")
    parser.add_argument("--bytes_per_char", type=str, help="The number of bytes to use to represent each character")
    parser.add_argument("--chars_per_sync", type=str, help="The number of characters to send on each sync event")
    parser.add_argument("--enable_local_beep", type=int, help="Whether to play a local auditory indicator when transcription starts/stops.")
    parser.add_argument("--rows", type=int, help="The number of rows on the board")
    parser.add_argument("--cols", type=int, help="The number of columns on the board")
    parser.add_argument("--window_duration_s", type=int, help="The length in seconds of the audio recording handed to the transcription algorithm")
    parser.add_argument("--cpu", type=int, help="If set to 1, use CPU instead of GPU")
    parser.add_argument("--use_builtin", type=int, help="If set to 1, use the text box built into the game.")
    parser.add_argument("--enable_uwu_filter", type=int, help="If set to 1, transcribed text will be passed through an uwu filter :3.")
    parser.add_argument("--remove_trailing_period", type=int, help="If set to 1, trailing period will be removed.")
    parser.add_argument("--enable_uppercase_filter", type=int, help="If set to 1, transcriptions will be converted to UPPERCASE.")
    parser.add_argument("--enable_lowercase_filter", type=int, help="If set to 1, transcriptions will be converted to lowercase.")
    parser.add_argument("--enable_profanity_filter", type=int, help="If set to 1, profanity in transcriptions will have their vowels replaced with asterisks. Only works in English.")
    parser.add_argument("--button", type=str, help="The controller button used to start/stop transcription. E.g. \"left joystick\"")
    parser.add_argument("--emotes_pickle", type=str, help="The path to emotes pickle. See emotes_v2.py for details.")
    parser.add_argument("--gpu_idx", type=str, help="The index of the GPU device to use. On single GPU systems, use 0.")
    parser.add_argument("--keybind", type=str, help="The keyboard hotkey to use to toggle transcription. For example, ctrl+shift+s")
    parser.add_argument("--reset_on_toggle", type=int, help="Whether to reset (clear) the transcript every time that transcription is toggled on.")
    parser.add_argument("--commit_fuzz_threshold", type=int, help="The edit distance under which two consecutive transcripts are considered to match.")
    parser.add_argument("--enable_debug_mode", type=int, help="If set to 1, print additional information to stdout while transcribing.")
    args = parser.parse_args()

    if not args.mic:
        args.mic = "index"

    if not args.language:
        args.language = "english"

    if not args.language_target:
        print("--language_target required", file=sys.stderr)

    if not args.model:
        args.model = "base"

    if not args.model_translation:
        print("--model_translation required.", file=sys.stderr)
        sys.exit(1)

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

    if not args.commit_fuzz_threshold:
        print("--commit_fuzz_threshold required", file=sys.stderr)
        sys.exit(1)

    args.gpu_idx = int(args.gpu_idx)

    window_duration_s = 120
    if args.window_duration_s:
        window_duration_s = int(args.window_duration_s)

    if args.cpu == 1:
        args.cpu = True
    else:
        args.cpu = False

    if args.reset_on_toggle == 1:
        args.reset_on_toggle = True
    else:
        args.reset_on_toggle = False

    if args.use_builtin == 1:
        args.use_builtin = True
    else:
        args.use_builtin = False

    if args.enable_uwu_filter == 1:
        args.enable_uwu_filter = True
    else:
        args.enable_uwu_filter = False

    if args.remove_trailing_period == 1:
        args.remove_trailing_period = True
    else:
        args.remove_trailing_period = False

    if args.enable_uppercase_filter == 1:
        args.enable_uppercase_filter = True
    else:
        args.enable_uppercase_filter = False

    if args.enable_lowercase_filter == 1:
        args.enable_lowercase_filter = True
    else:
        args.enable_lowercase_filter = False

    if args.enable_profanity_filter == 1:
        args.enable_profanity_filter = True
    else:
        args.enable_profanity_filter = False

    if args.enable_debug_mode == 1:
        args.enable_debug_mode = True
    else:
        args.enable_debug_mode = False

    estate = EmotesState()
    estate.load(args.emotes_pickle)

    generate_utils.config.BYTES_PER_CHAR = int(args.bytes_per_char)
    generate_utils.config.CHARS_PER_SYNC = int(args.chars_per_sync)
    generate_utils.config.BOARD_ROWS = int(args.rows)
    generate_utils.config.BOARD_COLS = int(args.cols)

    print(f"PATH: {os.environ['PATH']}")

    transcribeLoop(args.mic,
            args.language,
            args.language_target,
            args.model,
            args.model_translation,
            args.enable_local_beep,
            args.cpu, args.use_builtin,
            args.enable_uwu_filter,
            args.remove_trailing_period,
            args.enable_uppercase_filter,
            args.enable_lowercase_filter,
            args.enable_profanity_filter,
            args.enable_debug_mode,
            args.button,
            estate, window_duration_s,
            args.gpu_idx,
            args.keybind,
            args.reset_on_toggle,
            args.commit_fuzz_threshold)

