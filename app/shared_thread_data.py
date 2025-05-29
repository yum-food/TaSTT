import threading

class SharedThreadData:
    def __init__(self, cfg):
        self.word = ""
        self.word_lock = threading.Lock()
        self.exit_event = threading.Event()
        self.cfg = cfg

