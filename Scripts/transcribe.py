#!/usr/bin/env python3

from datetime import datetime
from emotes_v2 import EmotesState
from faster_whisper import WhisperModel
from functools import partial
from math import ceil, floor
from profanity_filter import ProfanityFilter
from sentence_splitter import split_text_into_sentences

import argparse
import app_config
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
import winsound

class AudioState:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        # This matches the framerate expected by whisper.
        self.RATE = 16000

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

        # The edit distance under which two consecutive transcripts are
        # considered to match. This affects how easily `preview_text`
        # gets appended to `text`.
        self.commit_fuzz_threshold = 1

        # If set, profanity in transcriptions will have their vowels replaced
        # with asterisks. Only works in English.
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

        # Audio events that should play. Input thread appends to this list,
        # audio feedback thread drains it.
        self.audio_events = []
        self.AUDIO_EVENT_TOGGLE_ON = 1
        self.AUDIO_EVENT_TOGGLE_OFF = 2
        self.AUDIO_EVENT_DISMISS = 3
        self.AUDIO_EVENT_UPDATE = 4

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

    # If buffer is getting long, tell the transcription loop to be more ready
    # to accept transcripts.
    fps = int(input_rate / audio_state.CHUNK)
    cur_len_s = len(audio_state.frames) / fps
    double_at_s = 3.0
    double_every_s = 1.5
    delta_s = cur_len_s - double_at_s
    n_doubles = ceil(delta_s / double_every_s)
    if n_doubles >= 1:
        audio_state.commit_fuzz_threshold = 2 ** n_doubles
    else:
        audio_state.commit_fuzz_threshold = 1

    if audio_state.drop_samples_till_i > 0:
        # Caller wants us to keep this many *whisper* samples, assuming that
        # we're getting one full frame every (1024 / 16KHz) seconds.
        # However we really get one full whisper frame a little slower, since
        # mics usually have a higher sample rate than 16 KHz (see decimation
        # code above).
        # The ratio of (mic sample rate) / (16KHz) is simply `keep_every`.
        n_frames_to_drop = float(audio_state.drop_samples_till_i) / audio_state.CHUNK
        n_frames_to_drop *= keep_every
        n_frames_to_drop_int = int(floor(n_frames_to_drop))
        if audio_state.cfg["enable_debug_mode"]:
            print(f"Dropping {n_frames_to_drop_int} frames, buffer has {len(audio_state.frames)} frames total")
        # First drop every whole chunk
        audio_state.frames = audio_state.frames[n_frames_to_drop_int:]
        # Then drop the part of the most recent chunk we no longer want
        if len(audio_state.frames) > 0:
            n_samples_to_drop = int(ceil((n_frames_to_drop % 1.0) * audio_state.CHUNK / keep_every))
            if audio_state.cfg["enable_debug_mode"]:
                print(f"Zeroing {n_samples_to_drop} samples in frame 0")
                print(f"Frame 0 has length {len(audio_state.frames[0])}")
            bytes_per_sample = 2
            audio_state.frames[0] = b'00' * n_samples_to_drop + audio_state.frames[0][n_samples_to_drop * bytes_per_sample:]
        audio_state.drop_samples_till_i = -1

    max_frames = int(input_rate * audio_state.MAX_LENGTH_S /
            audio_state.CHUNK)
    if len(audio_state.frames) > max_frames:
        audio_state.frames = audio_state.frames[-1 * max_frames:]

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
        if audio_state.cfg["enable_debug_mode"]:
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

    if audio_state.cfg["reset_on_toggle"]:
        if audio_state.cfg["enable_debug_mode"]:
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
            language = langcodes.find(audio_state.cfg["language"]).language,
            temperature = 0.0,
            log_prob_threshold = -0.8,
            vad_filter = True,
            condition_on_previous_text = True,
            without_timestamps = False)
    ranges = []
    for s in segments:
        if s.avg_logprob < -0.8 or s.no_speech_prob > 0.6:
            continue
        if audio_state.cfg["enable_debug_mode"]:
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

            if audio_state.cfg["enable_debug_mode"]:
                print(f"c0: {c0}, c1: {c1}, c2: {c2}, c3: {c3}")
            if c0_c1_d < max_edit and c1_c2_d < max_edit and c2_c3_d < max_edit:
                # For simplicity, completely reset saved audio ranges.
                audio_state.ranges_ls = []
                committed_text = c0[2]
                if audio_state.cfg["enable_debug_mode"]:
                    print(f"Dropping frames until {c0[1]}")
                n_samples_to_drop = int(ceil(audio_state.RATE * c0[1]))
                audio_state.drop_samples_till_i = n_samples_to_drop
                while audio_state.drop_samples_till_i == n_samples_to_drop:
                    # To prevent a race, wait until those audio samples are
                    # dropped by the microphone capture thread before returning.
                    time.sleep(.001)

    preview_text = ""
    for seg in ranges:
        if seg[2] == committed_text:
            continue
        preview_text += seg[2]

    return (committed_text, preview_text)

def transcribeAudio(audio_state):
    print("Ready!")
    last_transcribe_time = time.time()
    while audio_state.run_app == True:
        # Pace this out.
        # If `preview_text` is not empty, then we're still transcribing a
        # message, so don't enter the idle path.
        if audio_state.audio_paused and len(audio_state.preview_text) == 0:
            audio_state.sleepInterruptible(audio_state.transcribe_sleep_duration)

            audio_state.transcribe_no_change_count += 1
            # Increase sleep time. Code below will set sleep time back to minimum
            # if a change is detected.
            longer_sleep_dur = audio_state.transcribe_sleep_duration
            longer_sleep_dur += audio_state.transcribe_sleep_duration_min_s * (1.3**audio_state.transcribe_no_change_count)
            audio_state.transcribe_sleep_duration = min(
                    1000 * 1000,
                    longer_sleep_dur)

        text, preview_text = transcribe(audio_state, audio_state.cfg["model"], audio_state.frames,
                audio_state.cfg["use_cpu"])
        if len(text) == 0 and len(preview_text) == 0:
            if audio_state.cfg["enable_debug_mode"]:
                print("no transcription, spin ({} seconds)".format(time.time() - last_transcribe_time))
            last_transcribe_time = time.time()
            # Prevent audio buffer from holding more than a few seconds of silence
            # before real speech.
            audio_state.MAX_LENGTH_S = 5
            continue
        else:
            audio_state.MAX_LENGTH_S = 300

        if audio_state.drop_transcription:
            audio_state.drop_transcription = False
            audio_state.text = ""
            audio_state.preview_text = ""
            audio_state.filtered_text = ""
            if audio_state.cfg["enable_debug_mode"]:
                print("drop transcription ({} seconds)".format(time.time() - last_transcribe_time))
            last_transcribe_time = time.time()
            continue

        old_text = audio_state.text
        audio_state.text += text
        audio_state.preview_text = preview_text

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
        if audio_state.cfg["enable_debug_mode"]:
            print("Raw transcription ({} seconds): {}".format(
                now - last_transcribe_time,
                audio_state.text + audio_state.preview_text))
            last_transcribe_time = now
            print(f"Commit text: {text}")
            print(f"Preview text: {preview_text}")

        # Translate if requested.
        translated = audio_state.text + audio_state.preview_text
        if audio_state.language_target:
            whisper_lang = audio_state.cfg["language"]
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
        if audio_state.cfg["enable_uwu_filter"]:
            uwu_proc = subprocess.Popen(["Resources/Models/Uwwwu.exe", filtered_text],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            uwu_stdout, uwu_stderr = uwu_proc.communicate()
            uwu_text = uwu_stdout.decode("utf-8")
            uwu_text = uwu_text.replace("\n", "")
            uwu_text = uwu_text.replace("\r", "")
            filtered_text = uwu_text
        if audio_state.cfg["remove_trailing_period"]:
            if len(filtered_text) > 0 and filtered_text[-1] == '.' and not filtered_text.endswith("..."):
                filtered_text = filtered_text[0:len(filtered_text)-1]
        if audio_state.cfg["enable_uppercase_filter"]:
            filtered_text = filtered_text.upper()
        if audio_state.cfg["enable_lowercase_filter"]:
            filtered_text = filtered_text.lower()
        if audio_state.cfg["enable_profanity_filter"]:
            filtered_text = audio_state.profanity_filter.filter(filtered_text)
        audio_state.filtered_text = filtered_text

        now = time.time()
        print("Transcription ({} seconds): {}".format(
            now - last_transcribe_time,
            filtered_text))
        last_transcribe_time = now

        if old_text != audio_state.text + audio_state.preview_text:
            # We think the user said something, so  reset the amount of
            # time we sleep between transcriptions to the minimum.
            audio_state.transcribe_no_change_count = 0
            audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s

def sendAudio(audio_state):
    estate = EmotesState()
    while audio_state.run_app == True:
        text = audio_state.filtered_text
        if audio_state.cfg["use_builtin"]:
            ret = osc_ctrl.pageMessageBuiltin(audio_state.osc_state, text)
            time.sleep(1.5)
        else:
            ret = osc_ctrl.pageMessage(audio_state.osc_state, text, estate)
            is_paging = (ret == False)

            # Pace this out
            time.sleep(0.01)

def readKeyboardInput(audio_state):
    machine = keybind_event_machine.KeybindEventMachine(audio_state.cfg["keybind"])
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
            if not audio_state.cfg["use_builtin"]:
                osc_ctrl.toggleBoard(audio_state.osc_state.client, False)

            if audio_state.cfg["reset_on_toggle"]:
                if audio_state.cfg["enable_debug_mode"]:
                    print("Toggle detected, dropping transcript (1)")
                audio_state.drop_transcription = True
            else:
                if audio_state.cfg["enable_debug_mode"]:
                    print("Toggle detected, committing preview text (1)")
                audio_state.text += audio_state.preview_text
            audio_state.audio_paused = True
            resetAudioLocked(audio_state)
            resetDisplayLocked(audio_state)
            continue

        # Short hold
        if state == RECORD_STATE:
            state = PAUSE_STATE
            if not audio_state.cfg["use_builtin"]:
                osc_ctrl.lockWorld(audio_state.osc_state.client, True)
            audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s

            audio_state.audio_paused = True

            if audio_state.cfg["enable_local_beep"]:
                audio_state.audio_events.append(audio_state.AUDIO_EVENT_TOGGLE_OFF)
        elif state == PAUSE_STATE:
            state = RECORD_STATE
            if not audio_state.cfg["use_builtin"]:
                osc_ctrl.toggleBoard(audio_state.osc_state.client, True)
                osc_ctrl.lockWorld(audio_state.osc_state.client, False)
                osc_ctrl.ellipsis(audio_state.osc_state.client, True)
            if audio_state.cfg["reset_on_toggle"]:
                if audio_state.cfg["enable_debug_mode"]:
                    print("Toggle detected, dropping transcript (2)")
                audio_state.drop_transcription = True
            else:
                if audio_state.cfg["enable_debug_mode"]:
                    print("Toggle detected, committing preview text (2)")
                audio_state.text += audio_state.preview_text
            audio_state.audio_paused = False

            resetAudioLocked(audio_state)
            resetDisplayLocked(audio_state)

            if audio_state.cfg["enable_local_beep"]:
                audio_state.audio_events.append(audio_state.AUDIO_EVENT_TOGGLE_ON)


def audioFeedbackThread(audio_state):
    with open(os.path.abspath("Resources/Sounds/Noise_On_Quiet.wav"), "rb") as f:
        waveform0 = f.read()
    with open(os.path.abspath("Resources/Sounds/Noise_Off_Quiet.wav"), "rb") as f:
        waveform1 = f.read()
    with open(os.path.abspath("Resources/Sounds/Dismiss_Noise_Quiet.wav"), "rb") as f:
        waveform2 = f.read()
    with open(os.path.abspath("Resources/Sounds/KB_Noise_Off_Quiet.wav"), "rb") as f:
        waveform3 = f.read()
    while audio_state.run_app == True:
        time.sleep(0.01)

        if len(audio_state.audio_events) == 0:
            continue

        event = audio_state.audio_events[0]
        audio_state.audio_events = audio_state.audio_events[1:]

        waveform = waveform0
        if event == audio_state.AUDIO_EVENT_TOGGLE_ON:
            waveform = waveform0
        elif event == audio_state.AUDIO_EVENT_TOGGLE_OFF:
            waveform = waveform1
        elif event == audio_state.AUDIO_EVENT_DISMISS:
            waveform = waveform2
        elif event == audio_state.AUDIO_EVENT_UPDATE:
            waveform = waveform3
        winsound.PlaySound(waveform, winsound.SND_MEMORY)

def readControllerInput(audio_state):
    RECORD_STATE = 0
    PAUSE_STATE = 1
    state = PAUSE_STATE

    hand_id = audio_state.cfg["button"].split()[0]
    button_id = audio_state.cfg["button"].split()[1]

    # Rough description of state machine:
    #   Single short press: toggle transcription
    #   Medium press: dismiss custom chatbox
    #   Long press: update chatbox in place
    #   Medium press + long press: type transcription

    last_rising = time.time()
    last_medium_press_end = 0

    button_generator = steamvr.pollButtonPress(hand=hand_id, button=button_id)
    while audio_state.run_app == True:
        time.sleep(0.01)
        event = next(button_generator)

        if event.opcode == steamvr.EVENT_RISING_EDGE:
            last_rising = time.time()

            if state == PAUSE_STATE:
                resetAudioLocked(audio_state)
                resetDisplayLocked(audio_state)
                audio_state.drop_transcription = True
                audio_state.audio_paused = False

        elif event.opcode == steamvr.EVENT_FALLING_EDGE:
            now = time.time()
            if now - last_rising > 1.5:
                # Long press: treat as the end of transcription.
                state = PAUSE_STATE
                if not audio_state.cfg["use_builtin"]:
                    osc_ctrl.lockWorld(audio_state.osc_state.client, True)
                audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s
                audio_state.audio_paused = True

                if last_rising - last_medium_press_end < 1.0:
                    # Type transcription
                    if audio_state.cfg["enable_local_beep"]:
                        audio_state.audio_events.append(audio_state.AUDIO_EVENT_UPDATE)
                    keyboard.write(audio_state.filtered_text)
                else:
                    if audio_state.cfg["enable_local_beep"]:
                        audio_state.audio_events.append(audio_state.AUDIO_EVENT_TOGGLE_OFF)

            elif now - last_rising > 0.5:
                # Medium press
                last_medium_press_end = now
                state = PAUSE_STATE

                if audio_state.cfg["enable_local_beep"]:
                    audio_state.audio_events.append(audio_state.AUDIO_EVENT_DISMISS)

                if not audio_state.cfg["use_builtin"]:
                    osc_ctrl.toggleBoard(audio_state.osc_state.client, False)

                resetAudioLocked(audio_state)
                resetDisplayLocked(audio_state)
                audio_state.drop_transcription = True
                audio_state.audio_paused = True
            else:
                # Short hold
                if state == RECORD_STATE:
                    state = PAUSE_STATE
                    if not audio_state.cfg["use_builtin"]:
                        osc_ctrl.lockWorld(audio_state.osc_state.client, True)
                    audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s

                    audio_state.audio_paused = True

                    if audio_state.cfg["enable_local_beep"]:
                        audio_state.audio_events.append(audio_state.AUDIO_EVENT_TOGGLE_OFF)
                elif state == PAUSE_STATE:
                    state = RECORD_STATE
                    if not audio_state.cfg["use_builtin"]:
                        osc_ctrl.toggleBoard(audio_state.osc_state.client, True)
                        osc_ctrl.lockWorld(audio_state.osc_state.client, False)
                        osc_ctrl.ellipsis(audio_state.osc_state.client, True)
                    if audio_state.cfg["reset_on_toggle"]:
                        if audio_state.cfg["enable_debug_mode"]:
                            print("Toggle detected, dropping transcript (3)")
                        audio_state.drop_transcription = True
                    else:
                        if audio_state.cfg["enable_debug_mode"]:
                            print("Toggle detected, committing preview text (3)")
                        audio_state.text += audio_state.preview_text

                    resetAudioLocked(audio_state)
                    resetDisplayLocked(audio_state)

                    if audio_state.cfg["enable_local_beep"]:
                        audio_state.audio_events.append(audio_state.AUDIO_EVENT_TOGGLE_ON)

# model should correspond to one of the Whisper models defined in
# whisper/__init__.py. Examples: tiny, base, small, medium.
def transcribeLoop(config_path: str):
    cfg = app_config.getConfig(config_path)

    generate_utils.config.BYTES_PER_CHAR = int(cfg["bytes_per_char"])
    generate_utils.config.CHARS_PER_SYNC = int(cfg["chars_per_sync"])
    generate_utils.config.BOARD_ROWS = int(cfg["rows"])
    generate_utils.config.BOARD_COLS = int(cfg["cols"])

    audio_state = getMicStream(cfg["microphone"])
    audio_state.cfg = cfg

    # Set up profanity filter
    en_profanity_path = os.path.abspath("Resources/Profanity/en")
    audio_state.profanity_filter = ProfanityFilter(en_profanity_path)
    if cfg["enable_profanity_filter"]:
        audio_state.profanity_filter.load()

    lang_bits = cfg["language_target"].split(" | ")
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

        output_dir = "Resources/" + cfg["model_translation"]
        # Provided by ctranslate2 Python package
        cmd = "ct2-transformers-converter.exe --model facebook/" + \
                cfg["model_translation"] + " --output_dir " + output_dir

        print(f"Fetching translation algorithm ({cfg['model_translation']})")
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

        whisper_lang = cfg["language"]
        nllb_lang = lang_compat.whisper_to_nllb[whisper_lang]

        audio_state.tokenizer = transformers.AutoTokenizer.from_pretrained(
                "facebook/" + cfg["model_translation"],
                src_lang=nllb_lang)

        print(f"Translation ready to go")

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    model_root = os.path.join(dname, "Models", cfg["model"])

    print("Model {} will be saved to {}".format(cfg["model"], model_root))

    model_device = "cuda"
    if cfg["use_cpu"]:
        model_device = "cpu"

    download_it = os.path.exists(model_root)
    if download_it:
        cfg["model"] = model_root
    cfg["model"] = WhisperModel(cfg["model"],
            device = model_device,
            device_index = cfg["gpu_idx"],
            compute_type = "int8",
            download_root = model_root,
            local_files_only = download_it)

    transcribe_audio_thd = threading.Thread(target = transcribeAudio, args = [audio_state])
    transcribe_audio_thd.daemon = True
    transcribe_audio_thd.start()

    send_audio_thd = threading.Thread(target = sendAudio, args = [audio_state])
    send_audio_thd.daemon = True
    send_audio_thd.start()

    controller_input_thd = threading.Thread(target = readControllerInput, args = [audio_state])
    controller_input_thd.daemon = True
    controller_input_thd.start()

    audio_feedback_thd = threading.Thread(target = audioFeedbackThread, args = [audio_state])
    audio_feedback_thd.daemon = True
    audio_feedback_thd.start()

    keyboard_input_thd = threading.Thread(target = readKeyboardInput, args = [audio_state])
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
    audio_feedback_thd.join()
    keyboard_input_thd.join()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    print("args: {}".format(" ".join(sys.argv)))

    print(f"Set cwd to {os.getcwd()}")

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, help="Path to app config YAML file.")
    args = parser.parse_args()

    print(f"PATH: {os.environ['PATH']}")

    transcribeLoop(args.config)

