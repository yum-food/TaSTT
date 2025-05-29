from faster_whisper import WhisperModel
import langcodes
import numpy as np
import os
import pyaudio
from pydub import AudioSegment
from shared_thread_data import SharedThreadData
import sys
import time
import typing
import vad

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
        if which_mic == "index":
            target_str = "Digital Audio Interface"
        elif which_mic == "focusrite":
            target_str = "Focusrite"
        elif which_mic == "motu":
            target_str = "In 1-2 (MOTU M Series)"
        elif which_mic == "beyond":
            target_str = "Microphone (Beyond)"
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
                AudioStream.FPS) / 1000.0)
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

        model_str = cfg["model"]
        model_root = os.path.join(parent_dir, "Models",
                os.path.normpath(model_str))
        print(f"Model {cfg['model']} will be saved to {model_root}",
                file=sys.stderr)

        model_device = "cuda"
        if cfg["use_cpu"]:
            model_device = "cpu"

        already_downloaded = os.path.exists(model_root)

        self.model = WhisperModel(model_str,
                device = model_device,
                device_index = cfg["gpu_idx"],
                compute_type = cfg["compute_type"],
                download_root = model_root,
                local_files_only = already_downloaded)

    def transcribe(self, frames: bytes = None) -> typing.List[Segment]:
        if frames is None:
            frames = self.collector.getAudio()
        # Convert from signed 16-bit int [-32768, 32767] to signed 32-bit float on
        # [-1, 1].
        audio = np.frombuffer(frames,
                dtype=np.int16).flatten().astype(np.float32) / 32768.0

        t0 = time.time()
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
                if self.cfg["enable_debug_mode"]:
                    print(f"Drop probable hallucination (case 1) " +
                            f"(text='{s.text}', " +
                            f"no_speech_prob={s.no_speech_prob}, " +
                            f"avg_logprob={s.avg_logprob})", file=sys.stderr)
                continue
            # Another touchup targeted at the vexatious "thanks for watching!"
            # hallucination. This triggers a lot when listening to
            # instrumental/electronic music.
            if s.no_speech_prob > 0.15 and s.avg_logprob < -0.7:
                if self.cfg["enable_debug_mode"]:
                    print(f"Drop probable hallucination (case 2) " +
                            f"(text='{s.text}', " +
                            f"no_speech_prob={s.no_speech_prob}, " +
                            f"avg_logprob={s.avg_logprob})", file=sys.stderr)
                continue
            if self.cfg["enable_debug_mode"]:
                print(f"s get: {s}")
            if s.avg_logprob < -1.0:
                continue
            if s.compression_ratio > 2.4:
                continue
            res.append(Segment(s.text, s.start, s.end,
                self.collector.begin(),
                s.avg_logprob, s.no_speech_prob, s.compression_ratio))
        t1 = time.time()
        if self.cfg["enable_debug_mode"]:
            print(f"Transcription latency (s): {t1 - t0}")
        return res

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
        duration_s = self.collector.duration()
        start_ts = self.collector.begin()

        if has_audio and stable_cutoff:
            #print(f"stable cutoff get: {stable_cutoff}", file=sys.stderr)
            latency_s = self.collector.now() - self.collector.begin()
            duration_s = stable_cutoff / AudioStream.FPS
            start_ts = self.collector.begin()
            commit_audio = self.collector.dropAudioPrefixByFrames(stable_cutoff)

            segments = self.whisper.transcribe(commit_audio)
            delta = ''.join(s.transcript for s in segments)
            audio = self.collector.getAudio()
            if self.cfg["enable_debug_mode"]:
                for s in segments:
                    print(f"commit segment: {s}", file=sys.stderr)
                print(f"delta get: {delta}", file=sys.stderr)

            if False:
                ts = datetime.fromtimestamp(self.collector.now() - latency_s)
                filename = str(ts.strftime('%Y_%m_%d__%H-%M-%S')) + ".wav"
                saveAudio(commit_audio, filename)

        preview = ""
        if self.cfg["enable_previews"] and has_audio:
            segments = self.whisper.transcribe(audio)
            preview = "".join(s.transcript for s in segments)

        if not has_audio:
            #print("VAD detects no audio, skip transcription", file=sys.stderr)
            self.collector.keepLast(1.0)

        return TranscriptCommit(
                delta.strip(),
                preview.strip(),
                latency_s,
                audio=audio,
                duration_s=duration_s,
                start_ts=start_ts)

def transcriptionThread(shared_data: SharedThreadData):
    last_stable_commit = None

    stream = MicStream(shared_data.cfg["microphone"])
    collector = AudioCollector(stream)
    collector = NormalizingAudioCollector(collector)
    collector = CompressingAudioCollector(collector)
    whisper = Whisper(collector, shared_data.cfg)
    segmenter = AudioSegmenter(min_silence_ms=shared_data.cfg["min_silence_duration_ms"],
            max_speech_s=shared_data.cfg["max_speech_duration_s"])
    committer = VadCommitter(shared_data.cfg, collector, whisper, segmenter)

    transcript = ""
    preview = ""

    while not shared_data.exit_event.is_set():
        time.sleep(shared_data.cfg["transcription_loop_delay_ms"] / 1000.0);

        op = None

        commit = committer.getDelta()

        if len(commit.delta) > 0 or len(commit.preview) > 0:
            # Avoid re-sending text after long pauses. User controls the length
            # of the pause in the UI.
            if shared_data.cfg["reset_after_silence_s"] > 0:
                silence_duration = 0
                if last_stable_commit:
                    last_commit_end_ts = \
                            last_stable_commit.start_ts + \
                            last_stable_commit.duration_s
                    silence_duration = commit.start_ts - last_commit_end_ts
                if silence_duration > shared_data.cfg["reset_after_silence_s"]:
                    print(f"Resetting transcript after {silence_duration}-second "
                            "silence", file=sys.stderr)
                    transcript = ""
                    preview = ""
                if commit.delta:
                    last_stable_commit = commit

            # Hard-cap displayed transcript length at 4k characters to prevent
            # runaway memory use in UI. Keep the full transcript to avoid
            # breaking OSC pager.
            transcript = transcript[-4096:]
            def join_segments(a, b):
                if len(a) > 0 and a[-1] != ' ':
                    return a + ' ' + b
                else:
                    return a + b
            transcript = join_segments(transcript, commit.delta)
            preview = commit.preview

            try:
                print(f"Transcript: {transcript}")
            except UnicodeEncodeError:
                print("Failed to encode transcript - discarding delta",
                        file=sys.stderr)
                continue
            try:
                print(f"Preview: {preview}")
            except UnicodeEncodeError:
                print("Failed to encode preview - discarding", file=sys.stderr)

            with shared_data.word_lock:
                shared_data.word = join_segments(transcript, preview)

            if shared_data.cfg["enable_debug_mode"]:
                print(f"commit latency: {commit.latency_s}", file=sys.stderr)
                print(f"commit thresh: {commit.thresh_at_commit}",
                        file=sys.stderr)

        if len(transcript) > 0 and \
                (not transcript.endswith(' ')) and \
                (not commit.delta.startswith(' ')):
            commit.delta = ' ' + commit.delta
        if len(commit.delta) > 0 and \
                (not commit.delta.endswith(' ')) and \
                (not commit.preview.startswith(' ')):
            commit.preview = ' ' + commit.preview

