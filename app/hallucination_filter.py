import io
import joblib
from logger import log, log_err
import numpy as np
import pandas as pd
from pathlib import Path
import pronouncing
import re
import sys

def count_syllables(word):
    """Count syllables in a word using pronouncing library with regex fallback."""
    phones = pronouncing.phones_for_word(word.lower())
    return pronouncing.syllable_count(phones[0])
def text_syllable_count(text):
    """Count total syllables in text."""
    words = re.findall(r'\b\w+\b', text)
    return sum(count_syllables(word) for word in words)
class HallucinationFilter:
    """Filter for detecting hallucinated segments in speech-to-text output."""
    def __init__(self, model_path: Path = None):
        """
        Initialize the hallucination filter.
        Args:
            model_path: Optional path to the model file. If not provided,
                       uses the default path.
        """
        self.model = None
        self.threshold = None
        self.features = None
        # Get the project root directory
        app_root = Path(__file__).resolve().parent
        project_root = app_root.parent
        # Use provided path or default
        if model_path is None:
            model_path = project_root / "Models" / "thankyou_filter_gb.pkl"
        # Try to load the model
        log_err(f"Loading hallucination filter")
        bundle = joblib.load(model_path)
        self.model = bundle["model"]
        self.threshold = bundle["threshold"]
        self.features = bundle["features"]
        log_err(f"Loaded hallucination filter model from {model_path}")
    def is_hallucination(self, segment) -> bool:
        """
        Check if a segment is likely a hallucination.
        Returns False if model is not available.
        Args:
            segment: A segment object with attributes avg_logprob, audio_len_s,
                    no_speech_prob, compression_ratio, text, start, and end.
        Returns:
            bool: True if the segment is likely a hallucination, False otherwise.
        """
        # Calculate text-based features
        text = getattr(segment, 'text', '')
        duration = segment.audio_len_s
        raw_duration = segment.end_ts - segment.start_ts
        n_syllables = text_syllable_count(text)
        sps = n_syllables / duration
        raw_sps = n_syllables / raw_duration
        duration_ratio = raw_duration / duration
        X = pd.DataFrame([[
            segment.avg_logprob,
            segment.no_speech_prob,
            segment.compression_ratio,
            np.log1p(duration),
            np.log1p(sps),
            np.log1p(raw_duration),
            np.log1p(raw_sps),
            duration_ratio,
            segment.avg_logprob * duration
        ]], columns=self.features)
        # Get probability
        prob = self.model.predict_proba(X)[0, 1]
        return prob >= self.threshold
