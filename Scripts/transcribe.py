#!/usr/bin/env python3

import argparse
import copy
from datetime import datetime
import os
import osc_ctrl
from functools import partial
# python3 -m pip install pyaudio
# License: MIT.
import pyaudio
import numpy as np
# python3 -m pip install playsound==1.2.2
# License: MIT.
from playsound import playsound
import steamvr
import string_matcher
import sys
import threading
import time
import wave
# python3 -m pip install git+https://github.com/openai/whisper.git
# python3 -m pip install torch -f https://download.pytorch.org/whl/torch_stable.html
# License: MIT.
import whisper

class AudioState:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    # This matches the framerate expected by whisper.
    RATE = 16000

    # The maximum length that recordAudio() will put into frames before it
    # starts dropping from the start.
    MAX_LENGTH_S = 10
    MAX_LENGTH_S_WHISPER = 30
    # The minimum length that recordAudio() will wait for before saving audio.
    MIN_LENGTH_S = 1

    # PyAudio object
    p = None

    # PyAudio stream object
    stream = None

    text = ""
    committed_text = ""
    frames = []

    # Locks access to `text`.
    transcribe_lock = threading.Lock()

    # Locks access to `frames`, and audio stored on disk.
    audio_lock = threading.Lock()

    # Used to tell the threads when to stop.
    run_app = True

    transcribe_sleep_duration_min_s = 0.05
    transcribe_sleep_duration_max_s = 1.50
    transcribe_no_change_count = 0
    transcribe_sleep_duration = transcribe_sleep_duration_min_s

    tx_state = osc_ctrl.OscTxState()

    # The transcription thread transcribes without holding locks, then
    # blocks on it. Thus we need some way to tell the transcription
    # thread to drop that transcription.
    drop_transcription = False

    # The language the user is speaking in. Default is English but user may set
    # this to whatever they want.
    language = whisper.tokenizer.TO_LANGUAGE_CODE["english"]

    audio_paused = False

    osc_client = osc_ctrl.getClient()

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

    max_frames = int(input_rate * audio_state.MAX_LENGTH_S / audio_state.CHUNK)
    if len(audio_state.frames) > max_frames:
        audio_state.frames = audio_state.frames[-1 * max_frames :]

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

    audio_state.stream = audio_state.p.open(format=audio_state.FORMAT,
            channels=audio_state.CHANNELS, rate=input_rate,
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
    osc_ctrl.clear(audio_state.osc_client, audio_state.tx_state)

def resetAudio(audio_state):
    audio_state.transcribe_lock.acquire()
    audio_state.audio_lock.acquire()
    resetAudioLocked(audio_state)
    audio_state.audio_lock.release()
    audio_state.transcribe_lock.release()

# Transcribe the audio recorded in a file.
def transcribe(audio_state, model, frames):

    start_time = time.time()

    frames = audio_state.frames
    # Convert from signed 16-bit int [-32768, 32767] to signed 16-bit float on
    # [-1, 1].
    # We should technically acquire a lock to protect frames, but this is
    # really slow and in practice it doesn't make the app crash, so who cares.
    frames = np.asarray(audio_state.frames)
    audio = np.frombuffer(frames, np.int16).flatten().astype(np.float32) / 32768.0

    audio = whisper.pad_or_trim(audio, length = audio_state.RATE *
            audio_state.MAX_LENGTH_S_WHISPER)

    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    result = None
    #for temp in (0.00, 0.05, 0.10, 0.15, 0.20):
    #for temp in (0.00, 0.05):
    for temp in (0.00,):
        options = whisper.DecodingOptions(language = audio_state.language,
                beam_size = 5, temperature = temp, without_timestamps = True)
        result = whisper.decode(model, mel, options)

        if result.avg_logprob < -1.0:
            print("avg logprob: {}".format(result.avg_logprob))
            result = None
            continue

        if result.compression_ratio > 2.4:
            print("compression ratio: {}".format(result.compression_ratio))
            result = None
            continue

        if result.no_speech_prob > 0.60:
            print("no speech prob: {}".format(result.no_speech_prob))
            result = None
            continue

        result = result.text
        break

    return result

def transcribeAudio(audio_state, model):
    last_transcribe_time = time.time()
    while audio_state.run_app == True:
        # Pace this out
        time.sleep(audio_state.transcribe_sleep_duration)

        # Increase sleep time. Code below will set sleep time back to minimum
        # if a change is detected.
        if audio_state.transcribe_no_change_count < 10:
            audio_state.transcribe_no_change_count += 1
        longer_sleep_dur = audio_state.transcribe_sleep_duration
        longer_sleep_dur += audio_state.transcribe_sleep_duration_min_s * (1.3**audio_state.transcribe_no_change_count)
        audio_state.transcribe_sleep_duration = min(
                audio_state.transcribe_sleep_duration_max_s,
                longer_sleep_dur)

        text = transcribe(audio_state, model, audio_state.frames)
        if not text:
            print("no transcription, spin ({} seconds)".format(time.time() - last_transcribe_time))
            last_transcribe_time = time.time()
            continue

        if audio_state.drop_transcription:
            audio_state.drop_transcription = False
            print("drop transcription ({} seconds)".format(time.time() - last_transcribe_time))
            last_transcribe_time = time.time()
            continue

        words = ''.join(c for c in text.lower() if (c.isalpha() or c == " ")).split()

        now = time.time()
        print("Transcription ({} seconds): {}".format(
            now - last_transcribe_time,
            audio_state.text))
        last_transcribe_time = now

        old_text = audio_state.text

        audio_state.text = string_matcher.matchStrings(audio_state.text,
                text, window_size = 20)
        if old_text != audio_state.text:
            # We think the user said something, so  reset the amount of
            # time we sleep between transcriptions to the minimum.
            audio_state.transcribe_no_change_count = 0
            audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s

def sendAudio(audio_state):
    while audio_state.run_app == True:
        text = audio_state.committed_text + " " + audio_state.text
        ret = osc_ctrl.sendMessageLazy(audio_state.osc_client, text,
                audio_state.tx_state)
        is_paging = (ret == osc_ctrl.SEND_MSG_LAZY_SENT_NON_EMPTY)
        osc_ctrl.indicatePaging(audio_state.osc_client, is_paging)

        # Pace this out
        time.sleep(0.01)

def readControllerInput(audio_state):
    session = steamvr.SessionState()
    RECORD_STATE = 0
    PAUSE_STATE = 1
    state = PAUSE_STATE
    osc_ctrl.indicateSpeech(audio_state.osc_client, False)
    osc_ctrl.indicatePaging(audio_state.osc_client, False)

    last_rising = time.time()
    while audio_state.run_app == True:
        time.sleep(0.05)

        event = steamvr.pollButtonPress(session)

        if event == steamvr.EVENT_RISING_EDGE:
            last_rising = time.time()
        elif event == steamvr.EVENT_FALLING_EDGE:
            now = time.time()
            if now - last_rising > 0.5:
                # Long hold
                state = PAUSE_STATE
                osc_ctrl.indicateSpeech(audio_state.osc_client, False)
                osc_ctrl.toggleBoard(audio_state.osc_client, False)
                #playsound(os.path.abspath("../Sounds/Noise_Off.wav"))

                resetAudioLocked(audio_state)
                resetDisplayLocked(audio_state)
                audio_state.drop_transcription = True
                audio_state.audio_paused = True
            else:
                # Short hold
                if state == RECORD_STATE:
                    state = PAUSE_STATE
                    osc_ctrl.indicateSpeech(audio_state.osc_client, False)
                    osc_ctrl.lockWorld(audio_state.osc_client, True)

                    audio_state.audio_paused = True

                    playsound(os.path.abspath("../Sounds/Noise_Off.wav"))
                elif state == PAUSE_STATE:
                    state = RECORD_STATE
                    osc_ctrl.indicateSpeech(audio_state.osc_client, True)
                    osc_ctrl.toggleBoard(audio_state.osc_client, True)
                    osc_ctrl.lockWorld(audio_state.osc_client, False)
                    resetAudioLocked(audio_state)
                    resetDisplayLocked(audio_state)

                    audio_state.drop_transcription = True
                    audio_state.audio_paused = False

                    playsound(os.path.abspath("../Sounds/Noise_On.wav"))

# model should correspond to one of the Whisper models defined in
# whisper/__init__.py. Examples: tiny, base, small, medium.
def transcribeLoop(mic: str, language: str, model: str):
    audio_state = getMicStream(mic)
    audio_state.language = whisper.tokenizer.TO_LANGUAGE_CODE[language]

    print("Safe to start talking")

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    model_root = os.path.join(dname, "Models")

    print("Model {} will be saved to {}".format(model, model_root))
    model = whisper.load_model(model, download_root=model_root)

    transcribe_audio_thd = threading.Thread(target = transcribeAudio, args = [audio_state, model])
    transcribe_audio_thd.daemon = True
    transcribe_audio_thd.start()

    send_audio_thd = threading.Thread(target = sendAudio, args = [audio_state])
    send_audio_thd.daemon = True
    send_audio_thd.start()

    controller_input_thd = threading.Thread(target = readControllerInput, args = [audio_state])
    controller_input_thd.daemon = True
    controller_input_thd.start()

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

if __name__ == "__main__":
    # Set cwd to the directory holding the script
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    parser = argparse.ArgumentParser()
    parser.add_argument("--mic", type=str, help="Which mic to use. Options: index, focusrite. Default: index")
    parser.add_argument("--language", type=str, help="Which language to use. Ex: english, japanese, chinese, french, german.")
    parser.add_argument("--model", type=str, help="Which AI model to use. Ex: tiny, base, small, medium")
    args = parser.parse_args()

    if not args.mic:
        args.mic = "index"

    if not args.language:
        args.language = "english"

    if not args.model:
        args.language = "base"

    transcribeLoop(args.mic, args.language, args.model)

