import winsound
import os
import random
import time

def get_wav_files_in_cwd():
    """Returns a list of .wav files in the current working directory."""
    return [f for f in os.listdir() if f.endswith('.wav')]

# Pro tip: wrap this in a predicate
def play_random_wav(wav_files):
    """Plays a random .wav file from the provided list asynchronously."""
    random_file = random.choice(wav_files)
    winsound.PlaySound(random_file, winsound.SND_FILENAME | winsound.SND_ASYNC)

def probably_play_random_wav(wav_files):
    """Plays a random .wav file from the list. Probably."""
    if random.randint(1,3) != 1:
        play_random_wav(wav_files)

def main():
    wav_files = get_wav_files_in_cwd()
    if not wav_files:
        print("No .wav files found in the current directory.")
        return

    try:
        while True:
            probably_play_random_wav(wav_files)
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Program terminated by user.")
        winsound.PlaySound(None, winsound.SND_PURGE)  # Stop any ongoing asynchronous sounds

if __name__ == "__main__":
    main()

