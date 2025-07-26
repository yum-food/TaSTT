import io
import joblib
from logger import log, log_err
import numpy as np
import pandas as pd
from pathlib import Path
import sys


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
        self.features = bundle["features"]  # Extract feature names
        log_err(f"Loaded hallucination filter model from {model_path}")

    def is_thank_you_hallucination(self, segment) -> bool:
        """
        Check if a segment is likely a "Thank you" hallucination.
        Returns False if model is not available.

        Args:
            segment: A segment object with attributes avg_logprob, audio_len_s,
                    no_speech_prob, and compression_ratio.

        Returns:
            bool: True if the segment is likely a hallucination, False otherwise.
        """
        # Create DataFrame with proper feature names
        X = pd.DataFrame([[
            segment.avg_logprob,
            segment.audio_len_s,
            segment.no_speech_prob,
            segment.compression_ratio,
            np.log1p(segment.audio_len_s),
            segment.avg_logprob * segment.audio_len_s
        ]], columns=self.features)

        # Get probability
        prob = self.model.predict_proba(X)[0, 1]
        return prob >= self.threshold

