from datetime import datetime
from faster_whisper import WhisperModel
import json
import langcodes
from logger import log, log_err
import noisereduce as nr
import numpy as np
import os
from profanity_filter import ProfanityFilter
import pyaudio
from pydub import AudioSegment
from shared_thread_data import SharedThreadData
from silero_vad import load_silero_vad, get_speech_timestamps
import sys
import time
import typing
import wave
from hallucination_filter import HallucinationFilter

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_ROOT)

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

class MicStream(AudioStream):
    CHUNK_SZ = 1024

    def __init__(self, cfg: typing.Dict):
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

        which_mic = cfg["microphone"]

        if cfg["enable_debug_mode"]:
            log(f"Finding mic {which_mic}")
            self.dumpMicDevices()

        got_match = False
        device_index = -1
        if which_mic == "index":
            target_str = "Digital Audio Interface"
        elif which_mic == "focusrite":
            target_str = "Focusrite"
        elif which_mic == "motu":
            target_str = "In 1-2 (MOTU M Series)"
        elif which_mic == "beyond":
            target_str = "Microphone (Beyond)"
        else:
            if cfg["enable_debug_mode"]:
                log(f"Mic {which_mic} requested, treating it as a numerical " +
                        "device ID")
            device_index = int(which_mic)
            got_match = True
        if not got_match:
            info = self.p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            for i in range(0, numdevices):
                if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    device_name = self.p.get_device_info_by_host_api_device_index(0, i).get('name')
                    if target_str in device_name:
                        log(f"Got matching mic: {device_name}")
                        device_index = i
                        got_match = True
                        break
        if not got_match:
            raise KeyError(f"Mic {which_mic} not found")

        info = self.p.get_device_info_by_host_api_device_index(0, device_index)
        if cfg["enable_debug_mode"]:
            log(f"Found mic {which_mic}: {info['name']}")
        self.sample_rate = int(info['defaultSampleRate'])
        if cfg["enable_debug_mode"]:
            log(f"Mic sample rate: {self.sample_rate}")

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
                log("Input Device id ", i, " - ", device_name)

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
        n_bytes = int(dur_s * AudioStream.FPS) * self.stream.FRAME_SZ
        n_bytes = min(n_bytes, len(self.frames))
        cut_portion = self.frames[:n_bytes]
        self.frames = self.frames[n_bytes:]
        self.wall_ts += float(n_bytes / self.stream.FRAME_SZ) / self.stream.FPS
        return cut_portion

    def dropAudioPrefixByFrames(self, dur_frames: int) -> bytes:
        n_bytes = dur_frames * self.stream.FRAME_SZ
        n_bytes = min(n_bytes, len(self.frames))
        cut_portion = self.frames[:n_bytes]
        self.frames = self.frames[n_bytes:]
        self.wall_ts += float(n_bytes / self.stream.FRAME_SZ) / self.stream.FPS
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
        return len(self.frames) / (AudioStream.FPS * self.stream.FRAME_SZ)

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

class BoostingAudioCollector(AudioCollectorFilter):
    def __init__(self, parent: AudioCollector,
                 target_dBFS: float,
                 max_gain_dB: float,
                 cfg: typing.Dict):
        AudioCollectorFilter.__init__(self, parent)
        self.target_dBFS = target_dBFS
        self.max_gain_dB = max_gain_dB
        self.cfg = cfg

    def getAudio(self) -> bytes:
        audio = self.parent.getAudio()

        audio = AudioSegment(audio, sample_width=AudioStream.FRAME_SZ,
                frame_rate=AudioStream.FPS, channels=AudioStream.CHANNELS)
        gain = min(self.target_dBFS - audio.dBFS, self.max_gain_dB)
        if self.cfg["enable_debug_mode"]:
            log(f"Boosting audio by {gain} dB (from {audio.dBFS} to {audio.dBFS + gain})")
        audio = audio.apply_gain(gain)

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

class NoiseReducingAudioCollector(AudioCollectorFilter):
    def __init__(self, parent: AudioCollector, cfg: typing.Dict):
        AudioCollectorFilter.__init__(self, parent)
        self.cfg = cfg

    def getAudio(self) -> bytes:
        audio = self.parent.getAudio()
        audio_array = np.frombuffer(audio, dtype=np.int16).astype(np.float32)

        reduced_audio = nr.reduce_noise(
            y=audio_array,
            sr=AudioStream.FPS,
        )

        # Convert back to int16
        reduced_audio = np.clip(reduced_audio, -32768, 32767)
        frames = np.int16(reduced_audio).tobytes()

        return frames

class AudioSegmenter:
    def __init__(self,
            min_silence_ms=250,
            max_speech_s=5,
            min_speech_duration_ms=100):
        self.min_silence_ms = min_silence_ms
        self.max_speech_s = max_speech_s
        self.min_speech_duration_ms = min_speech_duration_ms

        # Load Silero VAD model
        self.model = load_silero_vad()

        self.min_silence_duration_ms = min_silence_ms
        self.max_speech_duration_s = max_speech_s
        self.min_speech_duration_ms = min_speech_duration_ms

    def segmentAudio(self, audio: bytes):
        # Convert audio bytes to numpy array expected by silero-vad
        audio_array = np.frombuffer(audio,
                dtype=np.int16).flatten().astype(np.float32) / 32768.0

        # Get speech timestamps using silero-vad
        # Note: silero-vad expects sample rate of 16000 Hz which matches AudioStream.FPS
        speech_timestamps = get_speech_timestamps(
            audio_array,
            self.model,
            sampling_rate=AudioStream.FPS,
            min_silence_duration_ms=self.min_silence_duration_ms,
            max_speech_duration_s=self.max_speech_duration_s,
            min_speech_duration_ms=self.min_speech_duration_ms,
            return_seconds=False  # We want frame indices, not seconds
        )

        return speech_timestamps

    # Returns the stable cutoff (if any) and whether there are any segments.
    def getStableCutoff(self, audio: bytes) -> typing.Tuple[int, bool]:
        min_delta_frames = int((self.min_silence_duration_ms *
                AudioStream.FPS) / 1000.0)
        cutoff = None

        last_end = None
        segments = self.segmentAudio(audio)

        for i in range(len(segments)):
            s = segments[i]

            if last_end:
                delta_frames = s['start'] - last_end
                if delta_frames > min_delta_frames:
                    cutoff = s['start']
            else:
                last_end = s['end']

            if i == len(segments) - 1:
                now = int(len(audio) / AudioStream.FRAME_SZ)
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
            compression_ratio: float,
            audio_len_s: float):
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
        self.audio_len_s = audio_len_s

    def __str__(self):
        ts = f"(ts: {self.start_ts}-{self.end_ts}) "

        wall_ts_start = datetime.utcfromtimestamp(self.start_ts + self.wall_ts).strftime('%H:%M:%S')
        wall_ts_end = datetime.utcfromtimestamp(self.end_ts + self.wall_ts).strftime('%H:%M:%S')
        wall_ts = f"(wall ts: {wall_ts_start}-{wall_ts_end}) "

        no_speech = f"(no_speech: {self.no_speech_prob}) "
        avg_logprob = f"(avg_logprob: {self.avg_logprob}) "
        max_len_s = f"(max_len_s: {self.audio_len_s}) "
        return f"{self.transcript} " + ts + wall_ts + no_speech + avg_logprob + max_len_s

def join_segments(a, b):
    if len(a) > 0 and a[-1] != ' ':
        return a + ' ' + b
    else:
        return a + b


class SegmentLogger:
    def __init__(self, cfg: typing.Dict):
        self.cfg = cfg
        self.enabled = cfg.get("enable_segment_logging", False)
        self.session_data = []
        self.log_file = None

        if self.enabled:
            log_dir = os.path.join(PROJECT_ROOT, "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Create file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = os.path.join(log_dir, f"session_debug_{timestamp}.json")
            log(f"Segment logging enabled. Logging to: {self.log_file}")

    def log_segment(self, segment: Segment, commit_type: str = "commit"):
        if not self.enabled:
            return

        segment_data = {
            "timestamp": datetime.now().isoformat(),
            "type": commit_type,
            "text": segment.transcript,
            "start_ts": segment.start_ts,
            "end_ts": segment.end_ts,
            "wall_ts": segment.wall_ts,
            "avg_logprob": segment.avg_logprob,
            "no_speech_prob": segment.no_speech_prob,
            "compression_ratio": segment.compression_ratio,
            "duration": segment.end_ts - segment.start_ts,
            "duration_sanity": segment.audio_len_s
        }

        self.session_data.append(segment_data)

        # Write to file incrementally
        try:
            with open(self.log_file, 'w') as f:
                json.dump({
                    "session_start": self.session_data[0]["timestamp"] if self.session_data else None,
                    "segments": self.session_data
                }, f, indent=2)
        except Exception as e:
            log_err(f"Error writing segment log: {e}")

    def close(self):
        if self.enabled and self.session_data:
            log(f"Session complete. Logged {len(self.session_data)} " + \
                    "segments to {self.log_file}")


class Whisper:
    def __init__(self,
            collector: AudioCollector,
            cfg: typing.Dict,
            segment_logger: SegmentLogger = None):
        self.collector = collector
        self.model = None
        self.cfg = cfg
        self.hallucination_filter = HallucinationFilter()
        self.segment_logger = segment_logger

        model_str = cfg["model"]
        model_root = os.path.join(PROJECT_ROOT, "Models",
                os.path.normpath(model_str))
        if cfg["enable_debug_mode"]:
            log(f"Model {cfg['model']} will be saved to {model_root}")

        model_device = "cuda"
        compute_type = cfg["compute_type"]
        if cfg["use_cpu"]:
            model_device = "cpu"
            compute_type = "int8"

        already_downloaded = os.path.exists(model_root)

        if not already_downloaded:
            log(f"Model {model_str} not already downloaded, downloading now...")

        self.model = WhisperModel(model_str,
                device = model_device,
                device_index = cfg["gpu_idx"],
                compute_type = compute_type,
                download_root = model_root,
                local_files_only = already_downloaded)

        self.context_window_chars = 200  # Keep last 200 chars of context
        self.recent_context = ""  # Store recent committed text

    def update_context(self, committed_text: str):
        """Update the context with recently committed text."""
        self.recent_context = join_segments(self.recent_context, committed_text).strip()
        # Drop half of the context window.
        if len(self.recent_context) > self.context_window_chars:
            words = self.recent_context.split()
            words = words[len(words)//2:]
            self.recent_context = ' '.join(words)

    def transcribe(self, frames: bytes = None) -> typing.List[Segment]:
        if frames is None:
            frames = self.collector.getAudio()

        # Convert audio to float32
        audio = np.frombuffer(frames,
                dtype=np.int16).flatten().astype(np.float32) / 32768.0
        audio_len_s = len(frames) / 16000.0

        # Build context-aware prompt
        prompt = self._build_prompt()

        if self.cfg["enable_debug_mode"]:
            log(f"Prompt: {prompt}")

        t0 = time.time()
        segments, info = self.model.transcribe(
                audio,
                language = langcodes.find(self.cfg["language"]).language,
                vad_filter = False,
                #temperature=0.0,
                without_timestamps = False,
                initial_prompt=prompt,
                beam_size=self.cfg.get("beam_size", 5),
                best_of=self.cfg.get("best_of", 5),
                condition_on_previous_text=True
        )
        res = []
        for s in segments:
            # Log raw segment before filtering
            if self.segment_logger:
                # Create a temporary segment object for logging
                raw_seg = Segment(s.text, s.start, s.end,
                    self.collector.begin(),
                    s.avg_logprob, s.no_speech_prob, s.compression_ratio,
                    audio_len_s)
                self.segment_logger.log_segment(raw_seg, "raw")
            # Sometimes the model reports a bum duration, breaking our filters.
            # Cap the segment length above by the length of the audio in.
            duration_s = min(s.end - s.start, audio_len_s)

            if self.cfg["enable_debug_mode"]:
                log(f"s get: {s}")
            if s.avg_logprob < -1.0:
                continue
            if s.compression_ratio > 2.4:
                continue

            # Create segment object
            seg = Segment(s.text, s.start, s.end,
                self.collector.begin(),
                s.avg_logprob, s.no_speech_prob, s.compression_ratio,
                audio_len_s)

            # Check with ML model for "Thank you" hallucinations
            if self.hallucination_filter.is_thank_you_hallucination(seg):
                if self.cfg["enable_debug_mode"]:
                    log(f"Drop probable hallucination (case 4) " +
                            f"(text='{s.text}', " +
                            f"no_speech_prob={s.no_speech_prob}, " +
                            f"avg_logprob={s.avg_logprob})")
                continue

            res.append(seg)
        t1 = time.time()
        if self.cfg["enable_debug_mode"]:
            log(f"Transcription latency (s): {t1 - t0}")
        return res

    def _build_prompt(self) -> str:
        """Build a context-aware prompt for Whisper."""
        user_prompt = self.cfg["user_prompt"]
        context_prompt = ""
        if self.recent_context and len(self.recent_context) > 0:
            context_prompt = f"Here is the context so far: {self.recent_context}"

        prompts = [user_prompt, context_prompt]
        prompts = [p for p in prompts if p and len(p) > 0]
        return " ".join(prompts)

class TranscriptCommit:
    def __init__(self,
            delta: str,
            preview: str,
            latency_s: float = None,
            thresh_at_commit: int = None,
            audio: bytes = None,
            duration_s: float = None,
            start_ts: float = None):
        self.delta = delta
        self.preview = preview
        self.latency_s = latency_s
        self.thresh_at_commit = thresh_at_commit
        self.audio = audio
        # Time at which the commit is generated
        self.ts = time.time()
        # Time corresponding to the start of the segment
        self.start_ts = start_ts
        # The duration of the audio segment, in seconds.
        self.duration_s = duration_s


def saveAudio(audio: bytes, path: str, cfg: typing.Dict):
    with wave.open(path, 'wb') as wf:
        if cfg["enable_debug_mode"]:
            log(f"Saving audio to {path}")
        wf.setnchannels(AudioStream.CHANNELS)
        wf.setsampwidth(AudioStream.FRAME_SZ)
        wf.setframerate(AudioStream.FPS)
        wf.writeframes(audio)


class VadCommitter:
    def __init__(self,
            cfg: typing.Dict,
            collector: AudioCollector,
            whisper: Whisper,
            segmenter: AudioSegmenter,
            segment_logger: SegmentLogger = None):
        self.cfg = cfg
        self.collector = collector
        self.whisper = whisper
        self.segmenter = segmenter
        self.segment_logger = segment_logger

    def getDelta(self) -> TranscriptCommit:
        audio = self.collector.getAudio()
        stable_cutoff, has_audio = self.segmenter.getStableCutoff(audio)

        delta = ""
        commit_audio = None
        latency_s = None
        duration_s = self.collector.duration()
        start_ts = self.collector.begin()

        if has_audio and stable_cutoff:
            latency_s = self.collector.now() - self.collector.begin()
            duration_s = stable_cutoff / AudioStream.FPS
            start_ts = self.collector.begin()

            # Get the filtered audio first, then extract the portion we need
            filtered_audio = self.collector.getAudio()
            commit_audio = filtered_audio[:stable_cutoff * AudioStream.FRAME_SZ]

            # Now drop the prefix from the collector
            self.collector.dropAudioPrefixByFrames(stable_cutoff)

            segments = self.whisper.transcribe(commit_audio)
            delta = ''.join(s.transcript for s in segments)

            # Update whisper's context with the committed text
            if delta.strip():
                self.whisper.update_context(delta.strip())

            audio = self.collector.getAudio()
            if self.cfg["enable_debug_mode"]:
                for s in segments:
                    log(f"commit segment: {s}")
                if len(delta) > 0:
                    log(f"delta get: {delta}")

            if self.cfg["save_audio"] and len(delta) > 0:
                ts = datetime.fromtimestamp(self.collector.now() - latency_s)
                sanitized_delta = ''.join(c for c in delta.strip() if c.isalnum() or c == ' ')
                filename = str(ts.strftime('%Y_%m_%d__%H-%M-%S')) + sanitized_delta + ".wav"
                audio_dir = os.path.join(PROJECT_ROOT, "audio")
                if not os.path.exists(audio_dir):
                    os.makedirs(audio_dir)
                saveAudio(commit_audio, os.path.join(audio_dir, filename), self.cfg)

        preview = ""
        if self.cfg["enable_previews"] and has_audio:
            segments = self.whisper.transcribe(audio)
            preview = "".join(s.transcript for s in segments)

        if not has_audio:
            self.collector.keepLast(1.0)

        return TranscriptCommit(
                delta.strip(),
                preview.strip(),
                latency_s,
                audio=audio,
                duration_s=duration_s,
                start_ts=start_ts)


class StreamingPlugin:
    def __init__(self):
        pass

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        return commit

    def stop(self):
        pass


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


class ProfanityPlugin(StreamingPlugin):
    def __init__(self, cfg):
        self.cfg = cfg
        self.filter = None
        if cfg["enable_profanity_filter"]:
            en_profanity_path = os.path.join(PROJECT_ROOT, "Third_Party/Profanity/en")
            try:
                self.filter = ProfanityFilter(en_profanity_path)
                self.filter.load()
            except Exception as e:
                log_err(f"Warning: Could not load profanity filter: {e}")
                self.filter = None

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        if self.cfg["enable_profanity_filter"] and self.filter:
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
                transcript = _remove_trailing_period(transcript)
            else:
                preview = _remove_trailing_period(preview)
        return transcript, preview


def transcriptionThread(shared_data: SharedThreadData):
    last_stable_commit = None

    stream = MicStream(shared_data.cfg)
    collector = AudioCollector(stream)
    collector = CompressingAudioCollector(collector)
    collector = BoostingAudioCollector(collector, -16.0, 24.0,
                                       shared_data.cfg)
    collector = NoiseReducingAudioCollector(collector, shared_data.cfg)
    #collector = NormalizingAudioCollector(collector)
    segment_logger = SegmentLogger(shared_data.cfg)
    whisper = Whisper(collector, shared_data.cfg, segment_logger)
    segmenter = AudioSegmenter(min_silence_ms=shared_data.cfg["min_silence_duration_ms"],
            max_speech_s=shared_data.cfg["max_speech_duration_s"],
            min_speech_duration_ms=shared_data.cfg["min_speech_duration_ms"])
    committer = VadCommitter(shared_data.cfg, collector, whisper, segmenter, segment_logger)

    plugins = []
    # plugins.append(TranslationPlugin(shared_data.cfg))  # Not implemented yet
    plugins.append(UppercasePlugin(shared_data.cfg))
    plugins.append(LowercasePlugin(shared_data.cfg))
    plugins.append(ProfanityPlugin(shared_data.cfg))
    # plugins.append(UwuPlugin(shared_data.cfg))  # Not implemented yet
    # plugins.append(BrowserSource(shared_data.cfg))  # Not implemented yet

    filters = []
    filters.append(TrailingPeriodFilter(shared_data.cfg))

    transcript = ""
    preview = ""

    with shared_data.word_lock:
        shared_data.stream = stream
        shared_data.collector = collector

    log(f"Ready to go!")

    while not shared_data.exit_event.is_set():
        time.sleep(shared_data.cfg["transcription_loop_delay_ms"] / 1000.0);

        op = None

        commit = committer.getDelta()

        with shared_data.word_lock:
            for plugin in plugins:
                commit = plugin.transform(commit)

            if len(commit.delta) > 0 or len(commit.preview) > 0:
                # Avoid re-sending text after long pauses
                if shared_data.cfg["reset_after_silence_s"] > 0:
                    silence_duration = 0
                    if last_stable_commit:
                        last_commit_end_ts = \
                                last_stable_commit.start_ts + \
                                last_stable_commit.duration_s
                        silence_duration = commit.start_ts - last_commit_end_ts
                    if silence_duration > shared_data.cfg["reset_after_silence_s"]:
                        if shared_data.cfg["enable_debug_mode"]:
                            log(f"Resetting transcript after {silence_duration}-second "
                                    "silence")
                        shared_data.transcript = ""
                        shared_data.preview = ""
                        whisper.recent_context = ""  # Reset context too
                    if commit.delta:
                        last_stable_commit = commit

                # Hard-cap displayed transcript length to prevent
                # runaway memory use in UI. Keep the full transcript to avoid
                # breaking OSC pager.
                if len(shared_data.transcript) >= 1024:
                    shared_data.transcript = shared_data.transcript[-512:]
                shared_data.transcript = \
                        join_segments(shared_data.transcript, commit.delta)
                shared_data.preview = commit.preview

                for filt in filters:
                    shared_data.transcript, shared_data.preview = \
                            filt.transform(shared_data.transcript,
                                           shared_data.preview)

                try:
                    log(f"Transcript: {shared_data.transcript}")
                except UnicodeEncodeError:
                    log_err("Failed to encode transcript - discarding delta")
                    continue
                try:
                    log(f"Preview: {shared_data.preview}")
                except UnicodeEncodeError:
                    log_err("Failed to encode preview - discarding")

                if shared_data.cfg["enable_debug_mode"]:
                    log(f"commit latency: {commit.latency_s}")
                    log(f"commit thresh: {commit.thresh_at_commit}")

            if len(shared_data.transcript) > 0 and \
                    (not shared_data.transcript.endswith(' ')) and \
                    (not commit.delta.startswith(' ')):
                commit.delta = ' ' + commit.delta
            if len(commit.delta) > 0 and \
                    (not commit.delta.endswith(' ')) and \
                    (not commit.preview.startswith(' ')):
                commit.preview = ' ' + commit.preview
    for plugin in plugins:
        plugin.stop()
    for filt in filters:
        filt.stop()
    segment_logger.close()

