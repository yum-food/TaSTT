from datetime import datetime
from emotes_v2 import EmotesState
from faster_whisper import WhisperModel
from functools import partial
from profanity_filter import ProfanityFilter
from pydub import AudioSegment
from sentence_splitter import split_text_into_sentences

import app_config
import argparse
import ctranslate2
import editdistance
import keybind_event_machine
import keyboard
import langcodes
import lang_compat
import math
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
import vad
import wave
import winsound

class ThreadControl:
    def __init__(self, cfg):
        self.cfg = cfg
        self.run_app = True

class AudioStream():
    FORMAT = pyaudio.paInt16
    # Size of each frame (audio sample), in bytes. If you change FORMAT, make
    # sure this stays up to date!
    FRAME_SZ = 2
    # Frames per second.
    FPS = 16000
    CHANNELS = 1
    def __init__(self):
        pass

    def getSamples(self) -> bytes:
        raise NotImplementedError("getSamples is not implemented!")

class DiskStream(AudioStream):
    def __init__(self, path: str):
        fmt = None
        if path.endswith(".mp3"):
            fmt = "mp3"
        elif path.endswith(".wav"):
            fmt = "wav"
        else:
            raise NotImplementedError(f"Requested file type {path} " + \
                    "is not supported")
        print(f"Loading audio data", file=sys.stderr)
        audio = AudioSegment.from_file(path, format=fmt)
        audio = audio.set_channels(1)
        # TODO(yum) replace manual decimation code with this!
        audio = audio.set_frame_rate(16000)
        frames = np.array(audio.get_array_of_samples())
        frames = np.int16(frames).tobytes()

        self.frames = frames

        print(f"Loaded data", file=sys.stderr)

    def getSamples(self) -> bytes:
        # Give out samples at a fixed rate to minimize
        # noise.
        give_s = 0.2
        nframes = int(give_s * AudioStream.FPS)
        frames = self.frames[0:nframes * AudioStream.FRAME_SZ];
        self.frames = self.frames[nframes * AudioStream.FRAME_SZ:]

        if len(frames) < nframes:
            frames += np.zeros(nframes - len(frames), dtype=np.int16).tobytes()

        return frames

class MicStream(AudioStream):
    CHUNK_SZ = 1024

    def __init__(self, which_mic: str):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.sample_rate = None
        # Each time pyaudio gives us audio data, it's in the form of a chunk of
        # samples. We keep these in a list to keep the audio callback as light
        # as possible. Whenever downstream layers want data, we collapse the
        # list into a single array of data (a bytes object).
        self.chunks = []
        # If set, incoming frames are simply discarded.
        self.paused = False

        print(f"Finding mic {which_mic}", file=sys.stderr)
        self.dumpMicDevices()

        got_match = False
        device_index = -1
        focusrite_str = "Focusrite"
        index_str = "Digital Audio Interface"
        if which_mic == "index":
            target_str = index_str
        elif which_mic == "focusrite":
            target_str = focusrite_str
        else:
            print(f"Mic {which_mic} requested, treating it as a numerical " +
                    "device ID", file=sys.stderr)
            device_index = int(which_mic)
            got_match = True
        if not got_match:
            info = self.p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            for i in range(0, numdevices):
                if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    device_name = self.p.get_device_info_by_host_api_device_index(0, i).get('name')
                    if target_str in device_name:
                        print(f"Got matching mic: {device_name}",
                                file=sys.stderr)
                        device_index = i
                        got_match = True
                        break
        if not got_match:
            raise KeyError(f"Mic {which_mic} not found")

        info = self.p.get_device_info_by_host_api_device_index(0, device_index)
        print(f"Found mic {which_mic}: {info['name']}", file=sys.stderr)
        self.sample_rate = int(info['defaultSampleRate'])
        print(f"Mic sample rate: {self.sample_rate}", file=sys.stderr)

        self.stream = self.p.open(
                rate=self.sample_rate,
                channels=AudioStream.CHANNELS,
                format=AudioStream.FORMAT,
                input=True,
                frames_per_buffer=MicStream.CHUNK_SZ,
                input_device_index=device_index,
                stream_callback=self.onAudioFramesAvailable)

        self.stream.start_stream()

        AudioStream.__init__(self)

    def pause(self, state: bool = True):
        self.paused = state

    def dumpMicDevices(self):
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        for i in range(0, numdevices):
            if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                device_name = self.p.get_device_info_by_host_api_device_index(0, i).get('name')
                print("Input Device id ", i, " - ", device_name)

    def onAudioFramesAvailable(self,
            frames,
            frame_count,
            time_info,
            status_flags):
        if self.paused:
            # Don't literally pause, just start returning silence. This allows
            # the `min_segment_age_s` check to work while paused.
            n_frames = int(frame_count * AudioStream.FPS /
                    float(self.sample_rate))
            self.chunks.append(np.zeros(n_frames,
                dtype=np.int16).tobytes())
            return (frames, pyaudio.paContinue)

        decimated = b''
        # In pyaudio, a `frame` is a single sample of audio data.
        frame_len = AudioStream.FRAME_SZ
        next_frame = 0.0
        # The mic probably has a higher sample rate than Whisper wants, so
        # decrease the sample rate by dropping samples. Note that this
        # algorithm only works if the mic's rate is higher than whisper's
        # expected rate.
        keep_every = float(self.sample_rate) / AudioStream.FPS
        for i in range(frame_count):
            if i >= next_frame:
                decimated += frames[i*frame_len:(i+1)*frame_len]
                next_frame += keep_every
        self.chunks.append(decimated)

        return (frames, pyaudio.paContinue)

    # Get audio data and the corresponding timestamp.
    def getSamples(self) -> bytes:
        chunks = self.chunks
        self.chunks = []
        result = b''.join(chunks)
        return result

class AudioCollector:
    def __init__(self, stream: AudioStream):
        self.stream = stream
        self.frames = b''
        # Note: by design, this is the only spot where we anchor our timestamps
        # against the real world. This is done to make it possible to profile
        # test cases which read from disk (at much faster than real speed) in
        # the same way that we profile real-time data.
        self.wall_ts = time.time()

    def getAudio(self) -> bytes:
        frames = self.stream.getSamples()
        if frames:
            self.frames += frames
        return self.frames

    def dropAudioPrefix(self, dur_s: float) -> bytes:
        n_bytes = int(dur_s * self.stream.FPS) * self.stream.FRAME_SZ
        n_bytes = min(n_bytes, len(self.frames))
        cut_portion = self.frames[:n_bytes]
        self.frames = self.frames[n_bytes:]
        self.wall_ts = self.wall_ts + self.duration()
        return cut_portion

    def dropAudioPrefixByFrames(self, dur_frames: int) -> bytes:
        n_bytes = dur_frames * self.stream.FRAME_SZ
        n_bytes = min(n_bytes, len(self.frames))
        cut_portion = self.frames[:n_bytes]
        self.frames = self.frames[n_bytes:]
        self.wall_ts = self.wall_ts + self.duration()
        return cut_portion

    def keepLast(self, dur_s: float) -> bytes:
        drop_len = max(0, self.duration() - dur_s)
        return self.dropAudioPrefix(drop_len)

    def dropAudio(self):
        self.wall_ts += self.duration()
        cut_portion = self.frames
        self.frames = b''
        return cut_portion

    def duration(self):
        return len(self.frames) / (self.stream.FPS * self.stream.FRAME_SZ)

    def begin(self):
        return self.wall_ts

    def now(self):
        return self.begin() + self.duration()

class AudioCollectorFilter:
    def __init__(self, parent: AudioCollector):
        self.parent = parent

    def getAudio(self) -> bytes:
        return self.parent.getAudio()
    def dropAudioPrefix(self, dur_s: float):
        return self.parent.dropAudioPrefix(dur_s)
    def dropAudioPrefixByFrames(self, dur_frames: int):
        return self.parent.dropAudioPrefixByFrames(dur_frames)
    def keepLast(self, dur_s):
        return self.parent.keepLast(dur_s)
    def dropAudio(self):
        return self.parent.dropAudio()
    def duration(self):
        return self.parent.duration()
    def begin(self):
        return self.parent.begin()
    def now(self):
        return self.parent.now()

# Audio collector that enforces a minimum length on its audio data.
class LengthEnforcingAudioCollector(AudioCollectorFilter):
    def __init__(self, parent: AudioCollector, min_duration_s: float):
        AudioCollectorFilter.__init__(self, parent)
        self.min_duration_s = min_duration_s

    def getAudio(self) -> bytes:
        audio = self.parent.getAudio()
        min_duration_frames = int(self.min_duration_s * AudioStream.FPS)
        pad_len_frames = max(0, min_duration_frames - int(len(audio) /
            AudioStream.FRAME_SZ))
        pad = np.zeros(pad_len_frames, dtype=np.int16).tobytes()
        return pad + audio

class NormalizingAudioCollector(AudioCollectorFilter):
    def __init__(self, parent: AudioCollector):
        AudioCollectorFilter.__init__(self, parent)

    def getAudio(self) -> bytes:
        audio = self.parent.getAudio()

        audio = AudioSegment(audio, sample_width=AudioStream.FRAME_SZ,
                frame_rate=AudioStream.FPS, channels=AudioStream.CHANNELS)
        audio = audio.normalize()

        frames = np.array(audio.get_array_of_samples())
        frames = np.int16(frames).tobytes()

        return frames

class CompressingAudioCollector(AudioCollectorFilter):
    def __init__(self, parent: AudioCollector):
        AudioCollectorFilter.__init__(self, parent)

    def getAudio(self) -> bytes:
        audio = self.parent.getAudio()

        audio = AudioSegment(audio, sample_width=AudioStream.FRAME_SZ,
                frame_rate=AudioStream.FPS, channels=AudioStream.CHANNELS)
        # subtle compression has a slight positive effect on my benchmark
        audio = audio.compress_dynamic_range(threshold=-10, ratio=2.0)

        frames = np.array(audio.get_array_of_samples())
        frames = np.int16(frames).tobytes()

        return frames

class AudioSegmenter:
    def __init__(self,
            min_silence_ms=250,
            max_speech_s=5):
        self.vad_options = vad.VadOptions(
                min_silence_duration_ms=min_silence_ms,
                max_speech_duration_s=max_speech_s)
        pass

    def segmentAudio(self, audio: bytes):
        audio = np.frombuffer(audio,
                dtype=np.int16).flatten().astype(np.float32) / 32768.0
        return vad.get_speech_timestamps(audio, vad_options=self.vad_options)

    # Returns the stable cutoff (if any) and whether there are any segments.
    def getStableCutoff(self, audio: bytes) -> typing.Tuple[int, bool]:
        min_delta_frames = int((self.vad_options.min_silence_duration_ms *
                AudioStream.FPS) / 1000)
        cutoff = None

        last_end = None
        segments = self.segmentAudio(audio)

        for i in range(len(segments)):
            s = segments[i]
            #print(f"s: {s}")
            #print(f"last_end: {last_end}")

            if last_end:
                delta_frames = s['start'] - last_end
                #print(f"delta frames: {delta_frames}")
                if delta_frames > min_delta_frames:
                    cutoff = s['start']
            else:
                last_end = s['end']

            if i == len(segments) - 1:
                now = int(len(audio) / AudioStream.FRAME_SZ)
                #print(f"now: {now}")
                #print(f"min d: {min_delta_frames}")
                delta_frames = now - s['end']
                if delta_frames > min_delta_frames:
                    cutoff = now - int(min_delta_frames / 2)

        return (cutoff, len(segments) > 0)

# A segment of transcribed audio. `start_ts` and `end_ts` are floating point
# number of seconds since the beginning of audio data.
class Segment:
    def __init__(self,
            transcript: str,
            start_ts: float,
            end_ts: float,
            wall_ts: float,
            avg_logprob: float,
            no_speech_prob: float,
            compression_ratio: float):
        self.transcript = transcript
        # start_ts, end_ts are timestamps in seconds relative to `wall_ts`.
        self.start_ts = start_ts
        self.end_ts = end_ts
        # wall_ts is the time.time() at which the oldest audio sample leading
        # to this transcript was collected.
        self.wall_ts = wall_ts
        self.avg_logprob = avg_logprob
        self.no_speech_prob = no_speech_prob
        self.compression_ratio = compression_ratio

    def __str__(self):
        ts = f"(ts: {self.start_ts}-{self.end_ts}) "

        wall_ts_start = datetime.utcfromtimestamp(self.start_ts + self.wall_ts).strftime('%H:%M:%S')
        wall_ts_end = datetime.utcfromtimestamp(self.end_ts + self.wall_ts).strftime('%H:%M:%S')
        wall_ts = f"(wall ts: {wall_ts_start}-{wall_ts_end}) "

        no_speech = f"(no_speech: {self.no_speech_prob}) "
        avg_logprob = f"(avg_logprob: {self.avg_logprob}) "
        return f"{self.transcript} " + ts + wall_ts + no_speech + avg_logprob

class Whisper:
    def __init__(self,
            collector: AudioCollector,
            cfg: typing.Dict):
        self.collector = collector
        self.model = None
        self.cfg = cfg

        abspath = os.path.abspath(__file__)
        my_dir = os.path.dirname(abspath)
        parent_dir = os.path.dirname(my_dir)

        model_root = os.path.join(parent_dir, "Models", cfg["model"])
        print(f"Model {cfg['model']} will be saved to {model_root}",
                file=sys.stderr)

        model_device = "cuda"
        if cfg["use_cpu"]:
            model_device = "cpu"

        download_it = os.path.exists(model_root)
        model_str = cfg["model"]
        if download_it:
            model_str = model_root
        self.model = WhisperModel(model_str,
                device = model_device,
                device_index = cfg["gpu_idx"],
                compute_type = "int8",
                download_root = model_root,
                local_files_only = download_it)

    def transcribe(self, frames: bytes = None) -> typing.List[Segment]:
        if frames is None:
            frames = self.collector.getAudio()
        # Convert from signed 16-bit int [-32768, 32767] to signed 32-bit float on
        # [-1, 1].
        audio = np.frombuffer(frames,
                dtype=np.int16).flatten().astype(np.float32) / 32768.0

        segments, info = self.model.transcribe(
                audio,
                language = langcodes.find(self.cfg["language"]).language,
                vad_filter = True,
                temperature=0.0,
                without_timestamps = False)
        res = []
        for s in segments:
            # Manual touchup. I see a decent number of hallucinations sneaking
            # in with high `no_speech_prob` and modest `avg_logprob`.
            if s.no_speech_prob > 0.6 and s.avg_logprob < -0.5:
                continue
            if cfg["enable_debug_mode"]:
                print(f"s get: {s}")
            if s.avg_logprob < -1.0:
                continue
            if s.compression_ratio > 2.4:
                continue
            res.append(Segment(s.text, s.start, s.end,
                self.collector.begin(),
                s.avg_logprob, s.no_speech_prob, s.compression_ratio))
        return res

class TranscriptCommit:
    def __init__(self,
            delta: str,
            preview: str,
            latency_s: int = None,
            thresh_at_commit: int = None,
            audio: bytes = None):
        self.delta = delta
        self.preview = preview
        self.latency_s = latency_s
        self.thresh_at_commit = thresh_at_commit
        self.audio = audio

def saveAudio(audio: bytes, path: str):
    with wave.open(path, 'wb') as wf:
        print(f"Saving audio to {path}", file=sys.stderr)
        wf.setnchannels(AudioStream.CHANNELS)
        wf.setsampwidth(AudioStream.FRAME_SZ)
        wf.setframerate(AudioStream.FPS)
        wf.writeframes(audio)

class VadCommitter:
    def __init__(self,
            cfg: typing.Dict,
            collector: AudioCollector,
            whisper: Whisper,
            segmenter: AudioSegmenter):
        self.cfg = cfg
        self.collector = collector
        self.whisper = whisper
        self.segmenter = segmenter

    def getDelta(self) -> TranscriptCommit:
        audio = self.collector.getAudio()
        stable_cutoff, has_audio = self.segmenter.getStableCutoff(audio)

        delta = ""
        commit_audio = None
        latency_s = None
        if has_audio and stable_cutoff:
            #print(f"stable cutoff get: {stable_cutoff}", file=sys.stderr)
            latency_s = self.collector.now() - self.collector.begin()
            commit_audio = self.collector.dropAudioPrefixByFrames(stable_cutoff)

            segments = self.whisper.transcribe(commit_audio)
            delta = ''.join(s.transcript for s in segments)
            audio = self.collector.getAudio()
            if cfg["enable_debug_mode"]:
                for s in segments:
                    print(f"commit segment: {s}", file=sys.stderr)
                print(f"delta get: {delta}", file=sys.stderr)

            #ts = datetime.fromtimestamp(self.collector.now() - latency_s)
            #filename = str(ts.strftime('%Y_%m_%d__%H-%M-%S')) + ".wav"
            #saveAudio(commit_audio, filename)

        preview = ""
        if self.cfg["enable_previews"] and has_audio:
            segments = self.whisper.transcribe(audio)
            preview = "".join(s.transcript for s in segments)

        if not has_audio:
            #print("VAD detects no audio, skip transcription", file=sys.stderr)
            self.collector.keepLast(1.0)

        return TranscriptCommit(
                delta,
                preview,
                latency_s,
                audio=audio)

def install_in_venv(pkgs: typing.List[str]) -> bool:
    pkgs_str = " ".join(pkgs)
    print(f"Installing {pkgs_str}")
    pip_proc = subprocess.Popen(
            f"Resources/Python/python.exe -m pip install {pkgs_str}".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    pip_stdout, pip_stderr = pip_proc.communicate()
    pip_stdout = pip_stdout.decode("utf-8")
    pip_stderr = pip_stderr.decode("utf-8")
    print(pip_stdout, file=sys.stderr)
    print(pip_stderr, file=sys.stderr)
    if pip_proc.returncode != 0:
        print(f"`pip install {pkgs_str}` exited with {pip_proc.returncode}",
                file=sys.stderr)

class StreamingPlugin:
    def __init__(self):
        pass

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        return commit

    def stop(self):
        pass

class TranslationPlugin(StreamingPlugin):
    def __init__(self, cfg):
        lang_bits = cfg["language_target"].split(" | ")
        self.cfg = cfg
        self.language_target = None
        self.translator = None
        self.tokenizer = None
        if len(lang_bits) != 2:
            return
        self.language_target = lang_bits[1]

        print("Translation requested", file=sys.stderr)
        if not install_in_venv(["torch", "sentencepiece"]):
            return

        output_dir = "Resources/" + cfg["model_translation"]
        # Provided by ctranslate2 Python package
        cmd = "ct2-transformers-converter.exe --model facebook/" + \
                cfg["model_translation"] + " --output_dir " + output_dir

        print(f"Fetching translation algorithm ({cfg['model_translation']})",
                file=sys.stderr)
        if not os.path.exists(output_dir):
            ct2_proc = subprocess.Popen(
                    cmd.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            ct2_stdout, ct2_stderr = ct2_proc.communicate()
            ct2_stdout = ct2_stdout.decode("utf-8")
            ct2_stderr = ct2_stderr.decode("utf-8")
            print(ct2_stdout, file=sys.stderr)
            print(ct2_stderr, file=sys.stderr)
            if ct2_proc.returncode != 0:
                print(f"Failed to get NLLB model: ct2 process exited with "
                        "{ct2_proc.returncode}", file=sys.stderr)
        print(f"Using model at {output_dir}", file=sys.stderr)

        self.translator = ctranslate2.Translator(output_dir)

        whisper_lang = cfg["language"]
        nllb_lang = lang_compat.whisper_to_nllb[whisper_lang]

        self.tokenizer = transformers.AutoTokenizer.from_pretrained(
                "facebook/" + cfg["model_translation"],
                src_lang=nllb_lang)

        print(f"Translation ready to go", file=sys.stderr)

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        if not self.language_target:
            return commit

        def _translate_text(text: str) -> str:

            whisper_lang = self.cfg["language"]
            nllb_lang = lang_compat.whisper_to_nllb[whisper_lang]
            ss_lang = lang_compat.nllb_to_ss[nllb_lang]
            sentences = split_text_into_sentences(text, language=ss_lang)

            translated_sentences = []
            for sentence in sentences:
                source = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(sentence))
                target_prefix = [self.language_target]
                results = self.translator.translate_batch([source], target_prefix=[target_prefix])
                target = results[0].hypotheses[0][1:]
                translated_sentence = self.tokenizer.decode(self.tokenizer.convert_tokens_to_ids(target))
                translated_sentences.append(translated_sentence)
            translated = " ".join(translated_sentences)
            return translated

        commit.delta = _translate_text(commit.delta)
        commit.preview = _translate_text(commit.preview)
        return commit

class LowercasePlugin(StreamingPlugin):
    def __init__(self, cfg):
        self.cfg = cfg

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        if self.cfg["enable_lowercase_filter"]:
            commit.delta = commit.delta.lower()
            commit.preview = commit.preview.lower()
        return commit

class UppercasePlugin(StreamingPlugin):
    def __init__(self, cfg):
        self.cfg = cfg

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        if self.cfg["enable_uppercase_filter"]:
            commit.delta = commit.delta.upper()
            commit.preview = commit.preview.upper()
        return commit

class UwuPlugin(StreamingPlugin):
    def __init__(self, cfg):
        self.cfg = cfg

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        if self.cfg["enable_uwu_filter"]:
            def _to_uwu(s: str) -> str:
                uwu_proc = subprocess.Popen(["Resources/Uwu/Uwwwu.exe", s],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                uwu_stdout, uwu_stderr = uwu_proc.communicate()
                uwu_text = uwu_stdout.decode("utf-8")
                uwu_text = uwu_text.replace("\n", "")
                uwu_text = uwu_text.replace("\r", "")
                if uwu_text.isspace():
                    return ""
                # Guarantee that the segment starts with a single space and
                # doesn't end with whitespace.
                uwu_text = " " + uwu_text.lstrip().rstrip()
                return uwu_text
            commit.delta = _to_uwu(commit.delta)
            commit.preview = _to_uwu(commit.preview)
        return commit

class ProfanityPlugin(StreamingPlugin):
    def __init__(self, cfg):
        self.cfg = cfg
        en_profanity_path = os.path.abspath("Resources/Profanity/en")
        self.filter = ProfanityFilter(en_profanity_path)
        if cfg["enable_profanity_filter"]:
            self.filter.load()

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        if self.cfg["enable_profanity_filter"]:
            commit.delta = self.filter.filter(commit.delta)
            commit.preview = self.filter.filter(commit.preview)
        return commit

class PresentationFilter:
    def __init__(self):
        pass

    def transform(self, transcript: str, preview: str) -> typing.Tuple[str, str]:
        return transcript, preview

    def stop(self):
        pass

class TrailingPeriodFilter(PresentationFilter):
    def __init__(self, cfg):
        self.cfg = cfg

    def transform(self, transcript: str, preview: str) -> typing.Tuple[str, str]:
        if self.cfg["remove_trailing_period"]:
            def _remove_trailing_period(s: str) -> str:
                if len(s) > 0 and s[-1] == '.' and not s.endswith("..."):
                    s = s[0:len(s)-1]
                return s
            if len(preview) == 0:
                print("here")
                transcript = _remove_trailing_period(transcript)
            else:
                print("there")
                preview = _remove_trailing_period(preview)
        return transcript, preview

class OscPager:
    def __init__(self, cfg):
        self.osc_state = osc_ctrl.OscState(cfg["chars_per_sync"],
                cfg["rows"],
                cfg["cols"],
                cfg["bytes_per_char"])
        self.cfg = cfg
        self.next_sync_window = time.time()

    def page(self, text):
        if self.cfg["use_builtin"]:
            osc_ctrl.pageMessageBuiltin(self.cfg, self.osc_state, text)
            self.bumpSyncWindow(amount_s=1.5)
        else:
            osc_ctrl.pageMessage(self.cfg, self.osc_state, text, EmotesState())
            self.bumpSyncWindow()

    def bumpSyncWindow(self, amount_s=osc_ctrl.SYNC_DELAY_S):
        self.next_sync_window = time.time() + amount_s

    def getSyncWindow(self):
        while time.time() < self.next_sync_window:
            time.sleep(0.01)

    def clear(self):
        osc_ctrl.clear(self.osc_state)
        self.bumpSyncWindow()

    def toggleBoard(self, state: bool):
        osc_ctrl.toggleBoard(self.osc_state.client, state)
        self.bumpSyncWindow()

    def lockWorld(self, state: bool):
        osc_ctrl.lockWorld(self.osc_state.client, state)
        self.bumpSyncWindow()

    def ellipsis(self, state: bool):
        osc_ctrl.ellipsis(self.osc_state.client, state)
        self.bumpSyncWindow()

def evaluate(cfg,
        audio_path: str,
        control_path: str):
    stream = DiskStream(audio_path)

    collector = AudioCollector(stream)
    collector = CompressingAudioCollector(collector)
    whisper = Whisper(collector, cfg)
    segmenter = AudioSegmenter(min_silence_ms=250)
    committer = VadCommitter(cfg, collector, whisper, segmenter)
    transcript = ""
    commits = []
    last_commit_ts = None

    while True:
        time.sleep(.005)

        commit = committer.getDelta()

        if last_commit_ts != None and collector.now() - last_commit_ts > 30:
            break

        if len(commit.delta) > 0:
            print(f"Commit latency: {commit.latency_s}", file=sys.stderr)
            commits.append(commit)
            last_commit_ts = collector.now()

        transcript += commit.delta
        preview = commit.preview

        if False and len(commit.delta):
            print(f"transcript: {transcript}", file=sys.stderr)
            print(f"commit latency: {commit.latency_s}", file=sys.stderr)
            print(f"commit thresh: {commit.thresh_at_commit}", file=sys.stderr)

    with open(control_path, "r") as f:
        control = f.read()
    normalizer = EnglishTextNormalizer()
    control = normalizer(control)
    experiment = normalizer(transcript)

    sum_latency = 0
    for commit in commits:
        sum_latency += commit.latency_s
    avg_latency = sum_latency / len(commits)

    dist = editdistance.eval(control, experiment)

    print(f"RESULTS", file=sys.stderr)
    print(f"edit distance: {dist}", file=sys.stderr)
    print(f"avg latency: {avg_latency}", file=sys.stderr)
    print(f"num commits: {len(commits)}", file=sys.stderr)
    print(f"final transcript: {transcript}", file=sys.stderr)

    score = (3 + (dist/len(control)) * 100) * avg_latency
    print(f"score: {score}", file=sys.stderr)
    return score

def optimize(cfg,
        experiments: typing.List[typing.Tuple[str, str]]):

    install_in_venv(["git+https://github.com/openai/whisper.git",
        "scipy"])

    from scipy.optimize import minimize
    from whisper.normalizers import EnglishTextNormalizer

    def wrapper_to_optimize(x):
        s = 0
        for audio_path, control_path in experiments:
            s += evaluate(
                    cfg,
                    audio_path,
                    control_path,
                    int(x[0]),  # last_n_must_match
                    2**x[1],    # edit_thresh_min
                    (2**x[2])-1,# edit_thresh_grow_begin_s
                    x[3],       # edit_thresh_grow_halflife_s
                    x[4]        # min_segment_age_s
                    )
        return s

    initial_guess = [2.3, 1, 1.75, 1.5, 0.5]
    bounds = [
        (2, 3),    # last_n_must_match
        (1, 4),    # edit_thresh_min
        (0, 2.5), # edit_thresh_grow_begin_s
        (0.1, 2), # edit_thresh_grow_halflife_s
        (0, 3)     # min_segment_age_s
    ]

    result = minimize(
        wrapper_to_optimize,
        initial_guess,
        bounds=bounds,
        method='L-BFGS-B',
        options={"maxfun": int((60/.5)*12),
            "eps": 0.2},
    )

    optimized_params = result.x

    print("Optimized Parameters:", file=sys.stderr)
    print(f"last_n_must_match: {int(optimized_params[0])}", file=sys.stderr)
    print(f"edit_thresh_min: {optimized_params[1]}", file=sys.stderr)
    print(f"edit_thresh_grow_begin_s: {optimized_params[2]}", file=sys.stderr)
    print(f"edit_thresh_grow_halflife_s: {optimized_params[3]}",
            file=sys.stderr)
    print(f"min_segment_age_s: {optimized_params[4]}", file=sys.stderr)

    return optimized_params

def transcriptionThread(ctrl: ThreadControl):
    while ctrl.run_app:
        time.sleep(ctrl.cfg["transcription_loop_delay_ms"] / 1000.0);

        op = None

        commit = ctrl.committer.getDelta()

        for plugin in ctrl.plugins:
            commit = plugin.transform(commit)

        if len(commit.delta) > 0 or len(commit.preview) > 0:
            # Hard-cap displayed transcript length at 4k characters to prevent
            # runaway memory use in UI. Keep the full transcript to avoid
            # breaking OSC pager.
            transcript = ctrl.transcript[-4096:] + commit.delta
            preview = commit.preview

            for filt in ctrl.filters:
                transcript, preview = filt.transform(transcript, preview)

            try:
                print(f"Transcript: {transcript}")
            except UnicodeEncodeError:
                print("Failed to encode transcript - discarding delta")
                continue
            try:
                print(f"Preview: {preview}")
            except UnicodeEncodeError:
                print("Failed to encode preview - discarding")

            if cfg["enable_debug_mode"]:
                print(f"commit latency: {commit.latency_s}", file=sys.stderr)
                print(f"commit thresh: {commit.thresh_at_commit}",
                        file=sys.stderr)
            if len(commit.preview) > 0:
                print("Finalized: 0")
            else:
                print("Finalized: 1")

        ctrl.transcript += commit.delta
        ctrl.preview = ctrl.transcript + commit.preview
    for plugin in ctrl.plugins:
        plugin.stop()
    for filt in ctrl.filters:
        filt.stop()

def vrInputThread(ctrl: ThreadControl):
    RECORD_STATE = 0
    PAUSE_STATE = 1
    state = PAUSE_STATE

    hand_id = ctrl.cfg["button"].split()[0]
    button_id = ctrl.cfg["button"].split()[1]

    # Rough description of state machine:
    #   Single short press: toggle transcription
    #   Medium press: dismiss custom chatbox
    #   Long press: update chatbox in place
    #   Medium press + long press: type transcription

    last_rising = time.time()
    last_medium_press_end = 0

    waveform0 =  os.path.abspath("Resources/Sounds/Noise_On_Quiet.wav")
    waveform1 =  os.path.abspath("Resources/Sounds/Noise_Off_Quiet.wav")
    waveform2 =  os.path.abspath("Resources/Sounds/Dismiss_Noise_Quiet.wav")
    waveform3 =  os.path.abspath("Resources/Sounds/KB_Noise_Off_Quiet.wav")

    button_generator = steamvr.pollButtonPress(hand=hand_id, button=button_id,
            ctrl=ctrl)
    while ctrl.run_app:
        time.sleep(0.01)
        try:
            event = next(button_generator)
        except StopIteration:
            break

        if event.opcode == steamvr.EVENT_RISING_EDGE:
            last_rising = time.time()

            if state == PAUSE_STATE:
                ctrl.stream.pause(False)
                ctrl.stream.getSamples()

        elif event.opcode == steamvr.EVENT_FALLING_EDGE:
            now = time.time()
            if now - last_rising > 1.5:
                # Long press: treat as the end of transcription.
                state = PAUSE_STATE

                ctrl.stream.pause(True)

                if last_rising - last_medium_press_end < 1.0:
                    # Type transcription
                    if ctrl.cfg["enable_local_beep"]:
                        winsound.PlaySound(waveform3, winsound.SND_FILENAME | winsound.SND_ASYNC)
                        pass
                    # TODO(yum) this is broken! Audio is not being collected
                    # while paused anymore.
                    #keyboard.write(ctrl.preview)
                else:
                    if ctrl.cfg["enable_local_beep"]:
                        winsound.PlaySound(waveform1, winsound.SND_FILENAME | winsound.SND_ASYNC)
                        pass

            elif now - last_rising > 0.5:
                # Medium press
                print("CLEARING", file=sys.stderr)
                last_medium_press_end = now
                state = PAUSE_STATE

                if ctrl.cfg["enable_local_beep"]:
                    winsound.PlaySound(waveform2, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    pass

                if not ctrl.cfg["use_builtin"]:
                    ctrl.pager.getSyncWindow()
                    ctrl.pager.toggleBoard(False)

                # Flush the *entire* pipeline.
                ctrl.stream.pause(True)
                ctrl.stream.getSamples()
                ctrl.collector.dropAudio()
                ctrl.pager.clear()
                if ctrl.cfg["enable_lock_at_spawn"]:
                    # Give the board 0.5 seconds to disappear before unlocking from
                    # world space.
                    time.sleep(0.5)
                    ctrl.pager.lockWorld(False)
            else:
                # Short hold
                if state == RECORD_STATE:
                    print("PAUSED", file=sys.stderr)
                    state = PAUSE_STATE
                    if not ctrl.cfg["use_builtin"] and not ctrl.cfg["enable_lock_at_spawn"]:
                        ctrl.pager.getSyncWindow()
                        ctrl.pager.lockWorld(True)

                    ctrl.stream.pause(True)

                    if ctrl.cfg["enable_local_beep"]:
                        winsound.PlaySound(waveform1, winsound.SND_FILENAME | winsound.SND_ASYNC)
                        pass
                elif state == PAUSE_STATE:
                    print("RECORDING", file=sys.stderr)
                    state = RECORD_STATE
                    if not ctrl.cfg["use_builtin"]:
                        ctrl.pager.getSyncWindow()
                        ctrl.pager.toggleBoard(True)
                        ctrl.pager.lockWorld(ctrl.cfg["enable_lock_at_spawn"])
                        ctrl.pager.ellipsis(True)
                    if ctrl.cfg["reset_on_toggle"]:
                        if ctrl.cfg["enable_debug_mode"]:
                            print("Toggle detected, dropping transcript (3)",
                                    file=sys.stderr)
                        ctrl.transcript = ""
                        ctrl.preview = ""
                        #audio_state.drop_transcription = True
                    else:
                        if ctrl.cfg["enable_debug_mode"]:
                            print("Toggle detected, committing preview text (3)", file=sys.stderr)
                        #audio_state.text += audio_state.preview_text

                    ctrl.stream.pause(False)
                    ctrl.pager.clear()

                    if ctrl.cfg["enable_local_beep"]:
                        winsound.PlaySound(waveform0, winsound.SND_FILENAME | winsound.SND_ASYNC)
                        pass

def kbInputThread(ctrl: ThreadControl):
    machine = keybind_event_machine.KeybindEventMachine(ctrl.cfg["keybind"])
    last_press_time = 0

    # double pressing the keybind
    double_press_timeout = 0.5

    RECORD_STATE = 0
    PAUSE_STATE = 1
    state = PAUSE_STATE

    waveform0 =  os.path.abspath("Resources/Sounds/Noise_On_Quiet.wav")
    waveform1 =  os.path.abspath("Resources/Sounds/Noise_Off_Quiet.wav")
    waveform2 =  os.path.abspath("Resources/Sounds/Dismiss_Noise_Quiet.wav")
    waveform3 =  os.path.abspath("Resources/Sounds/KB_Noise_Off_Quiet.wav")

    while ctrl.run_app:
        time.sleep(0.01)

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
            print("CLEARING", file=sys.stderr)
            state = PAUSE_STATE

            if ctrl.cfg["enable_local_beep"]:
                winsound.PlaySound(waveform2, winsound.SND_FILENAME | winsound.SND_ASYNC)
                pass

            if not ctrl.cfg["use_builtin"]:
                ctrl.pager.getSyncWindow()
                ctrl.pager.toggleBoard(False)

            # Flush the *entire* pipeline.
            ctrl.stream.pause(True)
            ctrl.stream.getSamples()
            ctrl.collector.dropAudio()
            ctrl.pager.clear()
            if ctrl.cfg["enable_lock_at_spawn"]:
                # Give the board 0.5 seconds to disappear before unlocking from
                # world space.
                time.sleep(0.5)
                ctrl.pager.lockWorld(False)
            continue

        # Short hold
        if state == RECORD_STATE:
            print("PAUSED", file=sys.stderr)
            state = PAUSE_STATE
            if not ctrl.cfg["use_builtin"] and not ctrl.cfg["enable_lock_at_spawn"]:
                ctrl.pager.getSyncWindow()
                ctrl.pager.lockWorld(True)

            ctrl.stream.pause(True)

            if ctrl.cfg["enable_local_beep"]:
                winsound.PlaySound(waveform1, winsound.SND_FILENAME | winsound.SND_ASYNC)
                pass
        elif state == PAUSE_STATE:
            print("RECORDING", file=sys.stderr)
            state = RECORD_STATE
            if not ctrl.cfg["use_builtin"]:
                ctrl.pager.getSyncWindow()
                ctrl.pager.toggleBoard(True)
                ctrl.pager.lockWorld(ctrl.cfg["enable_lock_at_spawn"])
                ctrl.pager.ellipsis(True)
            if ctrl.cfg["reset_on_toggle"]:
                if ctrl.cfg["enable_debug_mode"]:
                    print("Toggle detected, dropping transcript (2)",
                            file=sys.stderr)
                ctrl.transcript = ""
                ctrl.preview = ""
            else:
                if ctrl.cfg["enable_debug_mode"]:
                    print("Toggle detected, committing preview text (2)",
                            file=sys.stderr)
                #audio_state.text += audio_state.preview_text

            ctrl.stream.pause(False)
            ctrl.pager.clear()

            if ctrl.cfg["enable_local_beep"]:
                winsound.PlaySound(waveform0, winsound.SND_FILENAME | winsound.SND_ASYNC)
                pass

def oscThread(ctrl: ThreadControl):
    while ctrl.run_app:
        ctrl.pager.getSyncWindow()
        ctrl.pager.page(ctrl.preview)
        time.sleep(0.01)

def run(cfg):
    stream = MicStream(cfg["microphone"])

    collector = AudioCollector(stream)
    #collector = LengthEnforcingAudioCollector(collector, 5.0)
    #collector = NormalizingAudioCollector(collector)
    collector = CompressingAudioCollector(collector)
    whisper = Whisper(collector, cfg)
    segmenter = AudioSegmenter(min_silence_ms=cfg["min_silence_duration_ms"],
            max_speech_s=cfg["max_speech_duration_s"])
    committer = VadCommitter(cfg, collector, whisper, segmenter)
    pager = OscPager(cfg)

    ctrl = ThreadControl(cfg)
    ctrl.stream = stream
    ctrl.collector = collector
    ctrl.whisper = whisper
    ctrl.committer = committer

    ctrl.plugins = []
    ctrl.plugins.append(TranslationPlugin(cfg))
    ctrl.plugins.append(UppercasePlugin(cfg))
    ctrl.plugins.append(LowercasePlugin(cfg))
    ctrl.plugins.append(ProfanityPlugin(cfg))
    ctrl.plugins.append(UwuPlugin(cfg))

    ctrl.filters = []
    ctrl.filters.append(TrailingPeriodFilter(cfg))

    ctrl.pager = pager
    ctrl.transcript = ""
    ctrl.preview = ""

    transcribe_audio_thd = threading.Thread(target=transcriptionThread, args=[ctrl])
    transcribe_audio_thd.daemon = True
    transcribe_audio_thd.start()

    vr_input_thd = threading.Thread(target=vrInputThread, args=[ctrl])
    vr_input_thd.daemon = True
    vr_input_thd.start()

    kb_input_thd = threading.Thread(target=kbInputThread, args=[ctrl])
    kb_input_thd.daemon = True
    kb_input_thd.start()

    osc_thd = threading.Thread(target=oscThread, args=[ctrl])
    osc_thd.daemon = True
    osc_thd.start()

    for line in sys.stdin:
        if "exit" in line or "quit" in line:
            print("Exit requested", file=sys.stderr)
            break

    ctrl.run_app = False
    print("Join transcription thread", file=sys.stderr)
    transcribe_audio_thd.join()
    print("Join vr input thread", file=sys.stderr)
    vr_input_thd.join()
    print("Join kb input thread", file=sys.stderr)
    kb_input_thd.join()
    print("Join osc thread", file=sys.stderr)
    osc_thd.join()
    print("Done", file=sys.stderr)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, help="Path to app config YAML file.")
    args = parser.parse_args()

    cfg = app_config.getConfig(args.config)

    experiments = [
            ("Evaluate/declaration_short/audio.mp3",
                "Evaluate/declaration_short/control.txt"),
            ("Evaluate/moist/audio.mp3",
                "Evaluate/moist/control.txt"),
            ("Evaluate/vei/audio.mp3",
                "Evaluate/vei/control.txt"),
            ]

    if False:
        sum = 0
        for audio, control in experiments:
            print(f"Run experiment {audio} :: {control}", file=sys.stderr)
            sum += evaluate(cfg, audio, control)
        print(f"Total score: {sum}", file=sys.stderr)
    else:
        #optimize(cfg, experiments)
        run(cfg)

