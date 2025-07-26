#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

try:
    import pronouncing
    HAS_PRONOUNCING = True
except ImportError:
    HAS_PRONOUNCING = False
    print("Warning: pronouncing library not found. Using regex fallback for syllable counting.")

def count_syllables(word):
    """Count syllables in a word using pronouncing library with regex fallback."""
    if HAS_PRONOUNCING:
        phones = pronouncing.phones_for_word(word.lower())
        if phones:
            return pronouncing.syllable_count(phones[0])
    
    # Fallback: count vowel groups
    vowel_groups = re.findall(r'[aeiouy]+', word, re.IGNORECASE)
    return max(1, len(vowel_groups))

def text_syllable_count(text):
    """Count total syllables in text."""
    words = re.findall(r'\b\w+\b', text)
    return sum(count_syllables(word) for word in words)

def load_segments(log_dir):
    """Load segments from JSON files."""
    segments = []

    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if not file.endswith('.json'):
                continue
            try:
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)

                for segment in data.get('segments', []):
                    if 'duration_sanity' not in segment:
                        continue

                    # Extract all available features
                    text = segment.get('text', '')
                    duration = segment.get('duration_sanity', 0)
                    
                    # Calculate raw duration from timestamps
                    start_ts = segment.get('start_ts', 0)
                    end_ts = segment.get('end_ts', 0)
                    raw_duration = end_ts - start_ts
                    
                    seg_data = {
                        'avg_logprob': segment.get('avg_logprob', 0),
                        'no_speech_prob': segment.get('no_speech_prob', 0),
                        'duration_sanity': duration,
                        'raw_duration': raw_duration,
                        'compression_ratio': segment.get('compression_ratio', 1),
                        'text': text
                    }

                    # Add speech rate features
                    n_words = len(re.findall(r'\b\w+\b', text))
                    n_chars = len(text)
                    n_syllables = text_syllable_count(text)
                    
                    seg_data['n_words'] = n_words
                    seg_data['n_syllables'] = n_syllables
                    seg_data['n_chars'] = n_chars
                    
                    # Calculate rates (words/syllables/chars per second)
                    seg_data['sps'] = n_syllables / duration
                    
                    # Calculate raw speech rate (using timestamp-based duration)
                    seg_data['raw_sps'] = n_syllables / raw_duration

                    # Add derived features
                    seg_data['log_duration'] = np.log1p(duration)
                    seg_data['logprob_duration_interaction'] = seg_data['avg_logprob'] * duration
                    seg_data['log_sps'] = np.log1p(seg_data['sps'])  # Log-scaled speech rate
                    seg_data['log_raw_duration'] = np.log1p(raw_duration)
                    seg_data['duration_ratio'] = raw_duration / duration if duration > 0 else 1.0
                    seg_data['raw_log_sps'] = np.log1p(seg_data['raw_sps'])  # Log-scaled raw speech rate

                    segments.append(seg_data)
            except Exception as e:
                print(f"Error loading {file}: {e}")

    return pd.DataFrame(segments)

def main():
    # Find logs directory
    log_dir = None
    for pattern in ["ui/dist/logs", "logs", "ui/dist/*/logs", "ui/dist/*/*/logs", "ui/dist/*/*/*/logs"]:
        paths = list(Path(".").glob(pattern))
        if paths:
            log_dir = str(paths[0])
            break

    if not log_dir:
        print("Could not find logs directory.")
        return

    # Load data
    print("Loading segments from logs...")
    df = load_segments(log_dir)

    if len(df) == 0:
        print("No segments found in logs!")
        return

    print(f"Loaded {len(df)} segments")

    # Print speech rate statistics
    print("\nSpeech rate statistics:")
    print(f"Syllables per second: mean={df['sps'].mean():.2f}, std={df['sps'].std():.2f}, max={df['sps'].max():.2f}")
    print(f"Raw syllables per second: mean={df['raw_sps'].mean():.2f}, std={df['raw_sps'].std():.2f}, max={df['raw_sps'].max():.2f}")
    print(f"Duration ratio (raw/sanity): mean={df['duration_ratio'].mean():.2f}, std={df['duration_ratio'].std():.2f}")
    
    # Step 1: Apply heuristic rules for seed labeling
    print("\nApplying heuristic rules for seed labeling...")
    
    # Conservative positive seeds (likely hallucinations)
    h_pos = (
        (df['avg_logprob'] < -0.8)           # This low of a logprob is almost always a hallucination
        | (df['compression_ratio'] > 2.3)    # High compressibility is usually a hallucination
        | (df['sps'] > 6)                    # No one speaks this fast
        | (df['sps'] < 0.5)                  # No one speaks this slow
    )
    
    # Conservative negative seeds (likely valid)
    h_neg = (
        (df['avg_logprob'] > -0.5)          # solid confidence drop
        & (df['compression_ratio'] < 1.2)
        & (df['sps'] < 6)
        & (df['sps'] > 0.5)
    )
    
    # Create seed labels (NaN for unlabeled)
    df['seed_label'] = np.where(h_pos, 1, 
                                np.where(h_neg, 0, np.nan))
    
    n_pos_seeds = (df['seed_label'] == 1).sum()
    n_neg_seeds = (df['seed_label'] == 0).sum()
    n_unlabeled = df['seed_label'].isna().sum()
    
    print(f"Seed labeling results:")
    print(f"  Positive seeds (hallucinations): {n_pos_seeds} ({n_pos_seeds/len(df):.1%})")
    print(f"  Negative seeds (valid): {n_neg_seeds} ({n_neg_seeds/len(df):.1%})")
    print(f"  Unlabeled: {n_unlabeled} ({n_unlabeled/len(df):.1%})")
    
    if n_pos_seeds == 0 or n_neg_seeds == 0:
        print("Warning: Not enough seed labels. Adjusting thresholds might help.")
        return
    
    # Show examples of positive seeds
    pos_seeds = df[df['seed_label'] == 1].head(5)
    if len(pos_seeds) > 0:
        print(f"\nExample positive seeds (likely hallucinations):")
        for _, seg in pos_seeds.iterrows():
            print(f"  SPS={seg['sps']:.1f}, logprob={seg['avg_logprob']:.2f}, text='{seg['text'][:50]}...'")

    # Define features
    features = ['avg_logprob', 'duration_sanity', 'no_speech_prob',
                'compression_ratio', 'log_duration', 'logprob_duration_interaction',
                'sps', 'log_sps', 'raw_duration', 'log_raw_duration', 
                'duration_ratio', 'raw_log_sps']

    X = df[features].values
    
    # Step 2: Train kNN on seed labels
    print("\nTraining k-NN classifier on seed labels...")
    
    labeled_mask = df['seed_label'].notna()
    X_seed = X[labeled_mask]
    y_seed = df.loc[labeled_mask, 'seed_label'].values.astype(int)
    
    # Create pipeline with scaling (important for kNN)
    knn_pipeline = Pipeline([
        ('scale', StandardScaler()),
        ('knn', KNeighborsClassifier(
            n_neighbors=15,          # adjust based on dataset size
            weights='distance'       # closer neighbors weigh more
        ))
    ])
    
    knn_pipeline.fit(X_seed, y_seed)
    
    # Step 3: Predict on all data
    print("Propagating labels to unlabeled segments...")
    
    # Get probabilities for all segments
    proba = knn_pipeline.predict_proba(X)[:, 1]  # probability of being hallucination
    df['knn_score'] = proba
    
    # Choose threshold - use 95th percentile of negative seeds
    neg_seed_scores = proba[df['seed_label'] == 0]
    threshold = max(0.05, np.percentile(neg_seed_scores, 95))
    
    print(f"\nChosen threshold: {threshold:.3f}")
    print(f"Based on 95th percentile of negative seed scores")
    
    # Apply threshold
    df['is_hallucination'] = (proba >= threshold).astype(int)
    
    # Print results
    n_hallucinations = df['is_hallucination'].sum()
    print(f"\nDetected hallucinations: {n_hallucinations} ({n_hallucinations/len(df):.1%})")
    
    # Step 4: Train final gradient boosting model on kNN labels
    print("\nTraining final Gradient Boosting classifier...")
    
    X_final = df[features]
    y_final = df['is_hallucination']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_final, y_final, test_size=0.3, stratify=y_final, random_state=42
    )
    
    # Train model
    model = GradientBoostingClassifier(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.05,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_proba_gb = model.predict_proba(X_test)[:, 1]
    
    print("\nFinal Model Performance:")
    print(classification_report(y_test, y_pred))
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    
    print(f"\nDetection rate (TPR): {tpr:.1%}")
    print(f"False positive rate (FPR): {fpr:.1%}")

    # Feature importance
    print("\nFeature Importance:")
    for feat, imp in sorted(zip(features, model.feature_importances_),
                           key=lambda x: x[1], reverse=True):
        print(f"  {feat}: {imp:.3f}")

    # Show example detections
    hallucination_examples = df[df['is_hallucination'] == 1].head(10)
    if len(hallucination_examples) > 0:
        print(f"\nExample detected hallucinations:")
        for _, seg in hallucination_examples.iterrows():
            print(f"  Score={seg['knn_score']:.3f}, SPS={seg['sps']:.1f}, text='{seg['text'][:60]}...'")

    # Save model
    model_dir = Path("Models")
    model_dir.mkdir(exist_ok=True)

    model_bundle = {
        "model": model,
        "threshold": 0.5,  # Using standard threshold since we trained on binary labels
        "features": features,
        "heuristic_thresholds": {
            "avg_logprob_high": -1.0,
            "compression_ratio_high": 2.4,
            "sps_high": 9.0
        }
    }

    output_path = model_dir / "hallucination_filter_gb.pkl"
    joblib.dump(model_bundle, output_path)
    print(f"\nModel saved to: {output_path}")

if __name__ == "__main__":
    main()
