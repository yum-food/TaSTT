import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def log(message):
    print(message, file=sys.stdout, flush=True)

def log_err(message):
    print(message, file=sys.stderr, flush=True)

