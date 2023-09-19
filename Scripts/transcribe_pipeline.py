import time


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
        self.ts = time.time()


class StreamingPlugin:
    def __init__(self):
        pass

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        return commit

    def stop(self):
        pass

