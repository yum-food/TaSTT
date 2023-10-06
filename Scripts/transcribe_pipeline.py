import time


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


class StreamingPlugin:
    def __init__(self):
        pass

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        return commit

    def stop(self):
        pass

