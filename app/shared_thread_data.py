import threading

class SharedThreadData:
    def __init__(self, cfg):
        self.transcript = ""
        self.preview = ""

        self.stream = None
        self.collector = None

        self.word_lock = threading.Lock()
        self.exit_event = threading.Event()
        self.cfg = cfg

