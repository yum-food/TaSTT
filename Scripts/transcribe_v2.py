from datetime import datetime
from faster_whisper import WhisperModel
from functools import partial
from pydub import AudioSegment
from whisper.normalizers import EnglishTextNormalizer
from scipy.optimize import minimize
from emotes_v2 import EmotesState

import app_config
import argparse
import editdistance
import langcodes
import math
import numpy as np
import os
import osc_ctrl
import pyaudio
import steamvr
import sys
import threading
import time
import typing

TRANSCRIBE_REQ_RESET_COMMITS = 0
TRANSCRIBE_REQ_WHOLE_BUFFER = 1

class ThreadControl:
    def __init__(self, cfg):
        self.cfg = cfg
        self.run_app = True
        self.transcribe_queue = []

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
                print("Input Device id ", i, " - ", device_name,
                        file=sys.stderr)

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

# A segment of transcribed audio. `start_ts` and `end_ts` are floating point
# number of seconds since the beginning of audio data.
class Segment:
    def __init__(self,
            transcript: str,
            start_ts: float,
            end_ts: float,
            wall_ts: float,
            avg_logprob: float,
            no_speech_prob: float):
        self.transcript = transcript
        # start_ts, end_ts are timestamps in seconds relative to `wall_ts`.
        self.start_ts = start_ts
        self.end_ts = end_ts
        # wall_ts is the time.time() at which the oldest audio sample leading
        # to this transcript was collected.
        self.wall_ts = wall_ts
        self.avg_logprob = avg_logprob
        self.no_speech_prob = no_speech_prob

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
        dname = os.path.dirname(abspath)

        model_root = os.path.join(dname, "Models", cfg["model"])
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

    def transcribe(self, frames = None) -> typing.List[Segment]:
        if frames is None:
            frames = self.collector.getAudio()
        # Convert from signed 16-bit int [-32768, 32767] to signed 32-bit float on
        # [-1, 1].
        audio = np.frombuffer(frames,
                dtype=np.int16).flatten().astype(np.float32) / 32768.0

        segments, info = self.model.transcribe(
                audio,
                beam_size = 5,
                language = langcodes.find(self.cfg["language"]).language,
                temperature = 0.0,
                log_prob_threshold = -1.0,
                vad_filter = True,
                without_timestamps = False)
        res = []
        for s in segments:
            res.append(Segment(s.text, s.start, s.end,
                self.collector.begin(),
                s.avg_logprob, s.no_speech_prob))
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

# Commits audio when the transcription layer repeats the same transcript,
# within some fuzzy match distance.
class FuzzyRepeatCommitter:
    def __init__(self,
            collector: AudioCollector,
            whisper: Whisper,
            last_n_must_match: int = 4,
            edit_thresh_min: float = 1,
            edit_thresh_grow_begin_s: float = 1.5,
            edit_thresh_grow_halflife_s: float = 0.5,
            min_segment_age_s: float = 0.5):
        self.collector = collector
        self.whisper = whisper
        # List of candidate segments. Once these all match, we commit the
        # corresponding audio data.
        self.candidates = []
        self.last_n_must_match = last_n_must_match
        self.edit_thresh_min = edit_thresh_min
        self.edit_thresh_grow_begin_s = edit_thresh_grow_begin_s
        self.edit_thresh_grow_halflife_s = edit_thresh_grow_halflife_s
        self.min_segment_age_s = min_segment_age_s

    def getDelta(self) -> TranscriptCommit:
        segments = self.whisper.transcribe()
        preview = ''.join(s.transcript for s in segments)

        if len(segments) == 0:
            self.collector.keepLast(1.0)
            return TranscriptCommit("", preview, None)

        s = segments[0]

        if len(self.candidates) < self.last_n_must_match:
            if len(self.candidates) == 0:
                self.candidates.append(s)
                return TranscriptCommit("", preview, None)
            s0 = self.candidates[0]
            if s.wall_ts != s0.wall_ts:
                print("Frames dropped, committer resetting candidates",
                        file=sys.stderr)
                self.candidates = []
                return TranscriptCommit("", preview, None)
            self.candidates.append(s)
            return TranscriptCommit("", preview, None)

        # Rule 1: last n segments must be within a certain edit distance of
        # each other. This edit distance starts low and increases exponentially
        # as the buffer size grows, thus allowing the check to get weaker under
        # compute pressure.
        edit_thresh = self.edit_thresh_min
        dt = self.collector.now() - (self.collector.begin() + s.start_ts)
        if dt > self.edit_thresh_grow_begin_s:
            dt -= self.edit_thresh_grow_begin_s
            edit_thresh = math.ceil(2**(dt /
                self.edit_thresh_grow_halflife_s))

        drop_candidates = 0
        for i in range(1, len(self.candidates)):
            prev = self.candidates[i-1]
            cur = self.candidates[i]
            dist = editdistance.eval(prev.transcript, cur.transcript)
            if dist > edit_thresh:
                drop_candidates = i
        if drop_candidates != 0:
            self.candidates = self.candidates[drop_candidates:]
            return TranscriptCommit("", preview, None)

        candidate = self.candidates[-1]

        # Rule 2: no committing segments that are fewer than the configured
        # number of seconds old.
        if self.collector.now() - (candidate.end_ts + candidate.wall_ts) < self.min_segment_age_s:
            self.candidates = []
            return TranscriptCommit("", preview, None)

        # Got a candidate! Commit it and return.
        self.candidates = []
        latency_s = self.collector.now() - (candidate.wall_ts + candidate.start_ts)
        # Measured to slightly improve performance in benchmark.
        audio = self.collector.dropAudioPrefix(candidate.end_ts + 0.10)

        return TranscriptCommit(candidate.transcript, preview, latency_s,
                thresh_at_commit=edit_thresh, audio=audio)

class OscPager:
    def __init__(self, cfg):
        self.osc_state = osc_ctrl.OscState(cfg["chars_per_sync"],
                cfg["rows"],
                cfg["cols"],
                cfg["bytes_per_char"])
        self.cfg = cfg
        self.next_sync_window = time.time()

    def page(self, text):
        now = time.time()
        if now < self.next_sync_window:
            return
        if self.cfg["use_builtin"]:
            osc_ctrl.pageMessageBuiltin(self.osc_state, text)
            self.next_sync_window = now + 1.5
        else:
            osc_ctrl.pageMessage(self.osc_state, text, EmotesState())
            self.next_sync_window = now + osc_ctrl.SYNC_DELAY_S

    def clear(self):
        osc_ctrl.clear(self.osc_state)

    def toggleBoard(self, state: bool):
        osc_ctrl.toggleBoard(self.osc_state.client, state)

    def lockWorld(self, state: bool):
        osc_ctrl.lockWorld(self.osc_state.client, state)

    def ellipsis(self, state: bool):
        osc_ctrl.ellipsis(self.osc_state.client, state)

def evaluate(cfg,
        audio_path: str,
        control_path: str,
        last_n_must_match: int = 3,
        edit_thresh_min: float = 1,
        edit_thresh_grow_begin_s: float = 1.5,
        edit_thresh_grow_halflife_s: float = 0.5,
        min_segment_age_s: float = 0.5
        ):
    stream = DiskStream(audio_path)

    collector = AudioCollector(stream)
    #collector = LengthEnforcingAudioCollector(collector, 5.0)
    #collector = NormalizingAudioCollector(collector)
    collector = CompressingAudioCollector(collector)
    whisper = Whisper(collector, cfg)
    com = FuzzyRepeatCommitter(collector, whisper,
            last_n_must_match=last_n_must_match,
            edit_thresh_min=edit_thresh_min,
            edit_thresh_grow_begin_s=edit_thresh_grow_begin_s,
            edit_thresh_grow_halflife_s=edit_thresh_grow_halflife_s,
            min_segment_age_s=min_segment_age_s)
    transcript = ""
    commits = []

    print(f"PARAMS")
    print(f"last_n_must_match: {last_n_must_match}")
    print(f"edit_thresh_min: {edit_thresh_min}")
    print(f"edit_thresh_grow_begin_s: {edit_thresh_grow_begin_s}")
    print(f"edit_thresh_grow_halflife_s: {edit_thresh_grow_halflife_s}")
    print(f"min_segment_age_s: {min_segment_age_s}")

    while len(stream.frames) > 0:
        commit = com.getDelta()

        if len(stream.frames) == 0:
            commit.delta = commit.preview
            commit.latency_s = 0

        if len(commit.delta) > 0:
            commits.append(commit)

        transcript += commit.delta
        preview = commit.preview

        if False and len(commit.delta):
            print(f"transcript: {transcript}")
            print(f"commit latency: {commit.latency_s}")
            print(f"commit thresh: {commit.thresh_at_commit}")

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

    print(f"RESULTS")
    print(f"edit distance: {dist}")
    print(f"avg latency: {avg_latency}")
    print(f"num commits: {len(commits)}")
    print(f"final transcript: {transcript}")

    score = (3 + (dist/len(control)) * 100) * avg_latency
    print(f"score: {score}")
    return score

def optimize(cfg,
        experiments: typing.List[typing.Tuple[str, str]]):

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

    print("Optimized Parameters:")
    print(f"last_n_must_match: {int(optimized_params[0])}")
    print(f"edit_thresh_min: {optimized_params[1]}")
    print(f"edit_thresh_grow_begin_s: {optimized_params[2]}")
    print(f"edit_thresh_grow_halflife_s: {optimized_params[3]}")
    print(f"min_segment_age_s: {optimized_params[4]}")

    return optimized_params

def transcriptionThread(ctrl: ThreadControl):
    commits = []
    while ctrl.run_app:
        op = None
        while len(ctrl.transcribe_queue) > 0:
            cur_op = ctrl.transcribe_queue[0]
            ctrl.transcribe_queue = ctrl.transcribe_queue[1:]
            if cur_op == TRANSCRIBE_REQ_RESET_COMMITS:
                commits = []
                op = None
                ctrl.transcribe_queue = []
                break
            elif cur_op == TRANSCRIBE_REQ_WHOLE_BUFFER:
                op = TRANSCRIBE_REQ_WHOLE_BUFFER
        if op == TRANSCRIBE_REQ_WHOLE_BUFFER:
            print("Retranscribing committed buffers", file=sys.stderr)
            audio = b''.join(commit.audio for commit in commits)
            segments = ctrl.whisper.transcribe(audio)
            # TODO support concatenation
            ctrl.transcript = "".join([s.transcript for s in segments])
            ctrl.preview = ctrl.transcript
            commits = []

        commit = ctrl.committer.getDelta()

        preview = commit.preview
        if False and len(preview) > 0:
            preview = "[" + preview + "]"

        if len(commit.delta):
            print(f"Transcript: {ctrl.transcript}{preview}")
            if cfg["enable_debug_mode"]:
                print(f"commit latency: {commit.latency_s}", file=sys.stderr)
                print(f"commit thresh: {commit.thresh_at_commit}", file=sys.stderr)
            commits.append(commit)

        ctrl.preview = ctrl.transcript + preview
        ctrl.transcript += commit.delta

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

    button_generator = steamvr.pollButtonPress(hand=hand_id, button=button_id)
    while ctrl.run_app:
        time.sleep(0.01)
        event = next(button_generator)

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
                if not ctrl.cfg["use_builtin"]:
                    ctrl.pager.lockWorld(True)

                ctrl.stream.pause(True)

                if last_rising - last_medium_press_end < 1.0:
                    # Type transcription
                    if ctrl.cfg["enable_local_beep"]:
                        #audio_state.audio_events.append(audio_state.AUDIO_EVENT_UPDATE)
                        pass
                    #keyboard.write(audio_state.filtered_text)
                else:
                    if ctrl.cfg["enable_local_beep"]:
                        #audio_state.audio_events.append(audio_state.AUDIO_EVENT_TOGGLE_OFF)
                        pass

            elif now - last_rising > 0.5:
                # Medium press
                print("CLEARING")
                last_medium_press_end = now
                state = PAUSE_STATE

                if ctrl.cfg["enable_local_beep"]:
                    #audio_state.audio_events.append(audio_state.AUDIO_EVENT_DISMISS)
                    pass

                if not ctrl.cfg["use_builtin"]:
                    ctrl.pager.toggleBoard(False)

                # Flush the *entire* pipeline.
                ctrl.stream.pause(True)
                ctrl.stream.getSamples()
                ctrl.collector.dropAudio()
                ctrl.pager.clear()
            else:
                # Short hold
                if state == RECORD_STATE:
                    print("PAUSED")
                    ctrl.transcribe_queue.append(TRANSCRIBE_REQ_WHOLE_BUFFER)
                    state = PAUSE_STATE
                    if not ctrl.cfg["use_builtin"]:
                        ctrl.pager.lockWorld(True)

                    ctrl.stream.pause(True)

                    if ctrl.cfg["enable_local_beep"]:
                        #audio_state.audio_events.append(audio_state.AUDIO_EVENT_TOGGLE_OFF)
                        pass
                elif state == PAUSE_STATE:
                    print("RECORDING", file=sys.stderr)
                    state = RECORD_STATE
                    ctrl.transcribe_queue.append(TRANSCRIBE_REQ_RESET_COMMITS)
                    if not ctrl.cfg["use_builtin"]:
                        ctrl.pager.toggleBoard(True)
                        ctrl.pager.lockWorld(False)
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
                        #audio_state.audio_events.append(audio_state.AUDIO_EVENT_TOGGLE_ON)
                        pass

def kbInputThread(ctrl: ThreadControl):
    while ctrl.run_app:
        time.sleep(0.01)

def oscThread(ctrl: ThreadControl):
    while ctrl.run_app:
        ctrl.pager.page(ctrl.preview)
        time.sleep(0.01)

def run(cfg):
    stream = MicStream(cfg["microphone"])

    collector = AudioCollector(stream)
    #collector = LengthEnforcingAudioCollector(collector, 5.0)
    #collector = NormalizingAudioCollector(collector)
    collector = CompressingAudioCollector(collector)
    whisper = Whisper(collector, cfg)
    committer = FuzzyRepeatCommitter(collector, whisper)
    pager = OscPager(cfg)

    ctrl = ThreadControl(cfg)
    ctrl.stream = stream
    ctrl.collector = collector
    ctrl.whisper = whisper
    ctrl.committer = committer
    ctrl.pager = pager
    ctrl.transcript = ""
    ctrl.transcribe_queue = []
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
            break

    ctrl.run_app = False
    transcribe_audio_thd.join()
    vr_input_thd.join()
    kb_input_thd.join()
    osc_thd.join()

if __name__ == "__main__":
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
            sum += evaluate(cfg, audio, control)
        print(f"Total score: {sum}")
    else:
        #optimize(cfg, experiments)
        run(cfg)


