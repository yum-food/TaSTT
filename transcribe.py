#!/usr/bin/env python3

import argparse
import copy
import string_matcher
import os
import osc_ctrl
# python3 -m pip install pydub
from pydub import AudioSegment as pydub_AudioSegment
from pydub import effects as pydub_effects
# python3 -m pip install pyaudio
import pyaudio
import sys
import threading
import time
import wave
# python3 -m pip install git+https://github.com/openai/whisper.git
# python3 -m pip install torch -f https://download.pytorch.org/whl/torch_stable.html
import whisper

class AudioState:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    # This matches the framerate expected by whisper.
    RATE = 16000

    # The maximum length that recordAudio() will put into frames before it
    # starts dropping from the start.
    MAX_LENGTH_S = 25
    # The minimum length that recordAudio() will wait for before saving audio.
    MIN_LENGTH_S = 1

    VOICE_AUDIO_FILENAME = "audio.wav"

    # PyAudio object
    p = None

    # PyAudio stream object
    stream = None

    frames = []
    frames_lock = threading.Lock()

    text = ""
    text_lock = threading.Lock()

    record_audio = True
    transcribe_audio = True
    send_audio = True

    transcribe_sleep_duration_min_s = 0.05
    transcribe_sleep_duration_max_s = 1.50
    transcribe_no_change_count = 0
    transcribe_sleep_duration = transcribe_sleep_duration_min_s
    # The language the user is speaking in.
    language = whisper.tokenizer.TO_LANGUAGE_CODE["english"]

    # When the user says `over`, we stop displaying new transcriptions until
    # they clear the board again.
    display_paused = False

    osc_client = osc_ctrl.getClient()

def getMicStream(which_mic):
    audio_state = AudioState()
    audio_state.p = pyaudio.PyAudio()

    print("Finding index mic...")
    got_match = False
    device_index = -1
    focusrite_str = "Focusrite"
    index_str = "Digital Audio Interface"
    if which_mic == "index":
        target_str = index_str
    elif which_mic == "focusrite":
        target_str = focusrite_str
    else:
        raise Exception("Unrecognized mic requested: {}".format(which_mic))
    while got_match == False:
        info = audio_state.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        for i in range(0, numdevices):
            if (audio_state.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                device_name = audio_state.p.get_device_info_by_host_api_device_index(0, i).get('name')
                print("Input Device id ", i, " - ", device_name)
                if target_str in device_name:
                    print("Got match: {}".format(device_name))
                    device_index = i
                    got_match = True
                    break
        if got_match == False:
            print("No match, sleeping")
            time.sleep(3)

    audio_state.stream = audio_state.p.open(format=audio_state.FORMAT,
            channels=audio_state.CHANNELS, rate=audio_state.RATE,
            input=True, frames_per_buffer=audio_state.CHUNK,
            input_device_index=device_index)

    return audio_state

# Continuously records audio as long as audio_state.record_audio is set.
def recordAudio(audio_state):
    print("Recording audio")
    while audio_state.record_audio:
        data = audio_state.stream.read(audio_state.CHUNK)

        audio_state.frames_lock.acquire()
        audio_state.frames.append(data)
        max_frames = int(audio_state.RATE * audio_state.MAX_LENGTH_S / audio_state.CHUNK)
        if len(audio_state.frames) > max_frames:
            audio_state.frames = audio_state.frames[-1 * max_frames :]
        audio_state.frames_lock.release()

    print("Done recording")

# Saves audio. recordAudio() may continue running while this takes place.
def saveAudio(audio_state, filename):
    min_frames = int(audio_state.RATE * audio_state.MIN_LENGTH_S / audio_state.CHUNK)
    if len(audio_state.frames) < min_frames:
        return

    wf = wave.open(filename, 'wb')
    wf.setnchannels(audio_state.CHANNELS)
    wf.setsampwidth(audio_state.p.get_sample_size(audio_state.FORMAT))
    wf.setframerate(audio_state.RATE)

    audio_state.frames_lock.acquire()
    frames = copy.deepcopy(audio_state.frames)
    audio_state.frames_lock.release()

    wf.writeframes(b''.join(frames))
    wf.close()

    # Normalize volume. This seems to make the neural net a little more
    # consistent.
    raw = pydub_AudioSegment.from_wav(filename)
    normalized = pydub_effects.normalize(raw)
    normalized.export(filename, format="wav")

def resetDiskAudioLocked(audio_state, filename):
    if os.path.isfile(audio_state.VOICE_AUDIO_FILENAME):
        # empty out the voice file
        open(audio_state.VOICE_AUDIO_FILENAME, "w").close()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(audio_state.CHANNELS)
    wf.setsampwidth(audio_state.p.get_sample_size(audio_state.FORMAT))
    wf.setframerate(audio_state.RATE)

    wf.writeframes(b''.join([]))
    wf.close()

def resetAudioLocked(audio_state):
    audio_state.frames = []
    audio_state.transcribe_no_change_count = 0
    audio_state.transcribe_sleep_duration = \
            audio_state.transcribe_sleep_duration_min_s

    resetDiskAudioLocked(audio_state, audio_state.VOICE_AUDIO_FILENAME)

    audio_state.text = ""
    osc_ctrl.clear(audio_state.osc_client)

def resetAudio(audio_state):
    audio_state.frames_lock.acquire()
    resetAudioLocked(audio_state)
    audio_state.frames_lock.release()

# Transcribe the audio recorded in a file.
def transcribe(audio_state, model, filename):

    audio_state.frames_lock.acquire()
    audio = whisper.load_audio(filename)
    audio_state.frames_lock.release()

    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    #options = whisper.DecodingOptions(language = "en",
    options = whisper.DecodingOptions(language = audio_state.language,
            beam_size = 5)
    result = whisper.decode(model, mel, options)

    if result.no_speech_prob > 0.15:
        print("no speech prob: {}".format(result.no_speech_prob))
        return None

    if result.avg_logprob < -1.0:
        print("avg logprob: {}".format(result.avg_logprob))
        return None

    if result.compression_ratio > 2.4:
        print("compression ratio: {}".format(result.compression_ratio))
        return None

    return result.text

def transcribeAudio(audio_state, model):
    while audio_state.transcribe_audio == True:
        # Pace this out
        print("sleep duration: {}".format(audio_state.transcribe_sleep_duration))
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
        print("next sleep duration: {}".format(audio_state.transcribe_sleep_duration))

        saveAudio(audio_state, audio_state.VOICE_AUDIO_FILENAME)

        if not os.path.isfile(audio_state.VOICE_AUDIO_FILENAME):
            time.sleep(0.1)
            continue

        text = transcribe(audio_state, model, audio_state.VOICE_AUDIO_FILENAME)
        if not text:
            continue

        audio_state.text_lock.acquire()

        words = ''.join(c for c in text.lower() if (c.isalpha() or c == " ")).split()

        if len(words) > 0:
            if words[-1] == "clear":
                resetAudio(audio_state)
                audio_state.text_lock.release()
                audio_state.display_paused = False
                continue
            elif words[-1] == "over":
                words = words[0:-1]
                audio_state.display_paused = True

        print("Transcription: {}".format(audio_state.text))

        old_text = audio_state.text
        #old_words = audio_state.text.split()
        #new_words = text.split()

        audio_state.text = string_matcher.matchStrings(audio_state.text,
                text, window_size = 5)
        if old_text != audio_state.text:
            # We think the user said something, so  reset the amount of
            # time we sleep between transcriptions to the minimum.
            audio_state.transcribe_no_change_count = 0
            audio_state.transcribe_sleep_duration = audio_state.transcribe_sleep_duration_min_s

        audio_state.text_lock.release()

def sendAudio(audio_state):
    tx_state = osc_ctrl.OscTxState()

    while audio_state.send_audio == True:
        if audio_state.display_paused:
            time.sleep(0.1)
            continue

        audio_state.text_lock.acquire()
        text = copy.deepcopy(audio_state.text)
        osc_ctrl.sendMessageLazy(audio_state.osc_client, text, tx_state)
        audio_state.text_lock.release()

        # Pace this out
        time.sleep(0.01)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mic", type=str, help="Which mic to use. Options: index, focusrite. Default: index")
    parser.add_argument("--language", type=str, help="Which language to use. Ex: english, japanese, chinese, french, german.")
    args = parser.parse_args()

    if not args.mic:
        args.mic = "index"

    if not args.language:
        args.language = "english"

    audio_state = getMicStream(args.mic)
    audio_state.language = whisper.tokenizer.TO_LANGUAGE_CODE[args.language]

    if os.path.isfile(audio_state.VOICE_AUDIO_FILENAME):
        # empty out the voice file
        open(audio_state.VOICE_AUDIO_FILENAME, "w").close()

    record_audio_thd = threading.Thread(target = recordAudio, args = [audio_state])
    record_audio_thd.daemon = True
    record_audio_thd.start()

    print("Safe to start talking")

    model = whisper.load_model("base")

    transcribe_audio_thd = threading.Thread(target = transcribeAudio, args = [audio_state, model])
    transcribe_audio_thd.daemon = True
    transcribe_audio_thd.start()

    send_audio_thd = threading.Thread(target = sendAudio, args = [audio_state])
    send_audio_thd.daemon = True
    send_audio_thd.start()

    print("Press enter or say 'Clear' to start a new message. Say 'Over' to " +
            "pause the display (saying 'Clear' resets it again).")
    for line in sys.stdin:
        resetAudio(audio_state)
        if "exit" in line or "quit" in line:
            break

    print("Joining threads")
    audio_state.record_audio = False
    audio_state.transcribe_audio = False
    record_audio_thd.join()
    transcribe_audio_thd.join()

