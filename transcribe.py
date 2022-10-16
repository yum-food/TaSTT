#!/usr/bin/env python3

import argparse
import copy
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

    # PyAudio object
    p = None

    # PyAudio stream object
    stream = None

    frames = []
    frames_lock = threading.Lock()

    text = ""
    # To improve temporal stability, we require two consecutive identical
    # transcriptions before "committing" to a transcription.
    text_candidate = ""
    text_lock = threading.Lock()

    record_audio = True
    transcribe_audio = True
    send_audio = True

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

    print("audio save")

def resetAudio(audio_state):
    audio_state.frames_lock.acquire()
    audio_state.frames = []
    audio_state.frames_lock.release()

# Transcribe the audio recorded in a file.
def transcribe(model, filename):

    audio = whisper.load_audio(filename)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    return result.text

def transcribeAudio(audio_state, model):
    while audio_state.transcribe_audio == True:
        saveAudio(audio_state, "audio.wav")

        if not os.path.isfile("audio.wav"):
            time.sleep(0.1)
            continue

        print("Beginning transcription")
        text = transcribe(model, "audio.wav")

        audio_state.text_lock.acquire()

        # We use a few heuristics to handle spurious mistranscriptions and to
        # handle events where we trim off the start of the audio clip.
        #   1. If we get 2 consecutive identical transcriptions, we commit to
        #       the transcription. This reduces the number of
        #       mistranscriptions by a lot.
        #   2. If the last transcription is a prefix of the current one, we
        #       immediately accept it, since the transcription is obviously
        #       somewhat stable.
        #   3. If the transcription is somewhat long and the
        #       first few characters change, we assume this is due to a
        #       trim event and immediately accept the transcription.
        if text == audio_state.text_candidate or text.startswith(audio_state.text_candidate):
            audio_state.text = text
        elif len(text) > 30 and len(audio_state.text_candidate) >= 10 and text[0:10] != audio_state.text_candidate[0:10]:
            audio_state.text = text

        audio_state.text_candidate = text

        audio_state.text_lock.release()

        print("Transcription: {}".format(audio_state.text))
        print("Candidate: {}".format(audio_state.text_candidate))

        # Pace this out
        time.sleep(0.05)

def sendAudio(audio_state):
    tx_state = osc_ctrl.OscTxState()
    while audio_state.send_audio == True:
        audio_state.text_lock.acquire()
        text = copy.deepcopy(audio_state.text)
        audio_state.text_lock.release()

        print("here")
        osc_ctrl.sendMessageLazy(audio_state.osc_client, text, tx_state)

        # Pace this out
        time.sleep(0.01)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mic", type=str, help="Which mic to use. Options: index, focusrite. Default: index")
    args = parser.parse_args()

    if not args.mic:
        args.mic = "index"

    if os.path.isfile("audio.wav"):
        os.remove("audio.wav")

    audio_state = getMicStream(args.mic)

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

    print("Press enter to start a new message")
    for line in sys.stdin:
        resetAudio(audio_state)
        if "exit" in line or "quit" in line:
            break

    print("Joining threads")
    audio_state.record_audio = False
    audio_state.transcribe_audio = False
    record_audio_thd.join()
    transcribe_audio_thd.join()

