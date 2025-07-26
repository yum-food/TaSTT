#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
import numpy as np
import pandas as pd
import pronouncing
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import warnings
from sklearn.model_selection import StratifiedKFold, cross_val_predict

def count_syllables(word):
    """Count syllables in a word using pronouncing library with regex fallback."""
    phones = pronouncing.phones_for_word(word.lower())
    return pronouncing.syllable_count(phones[0])

def text_syllable_count(text):
    """Count total syllables in text."""
    words = re.findall(r'\b\w+\b', text)
    return sum(count_syllables(word) for word in words)

def load_segments(log_dir):
    """Load segments from JSON files."""
    segments = []
    seen = set()  # To deduplicate identical segment metadata
    num_dupes = 0

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
                    n_syllables = text_syllable_count(text)
                    seg_data['sps'] = n_syllables / duration
                    seg_data['log_sps'] = np.log1p(seg_data['sps'])
                    seg_data['raw_sps'] = n_syllables / raw_duration
                    seg_data['log_raw_sps'] = np.log1p(seg_data['raw_sps'])

                    # Add derived features
                    seg_data['log_duration'] = np.log1p(duration)
                    seg_data['logprob_duration_interaction'] = seg_data['avg_logprob'] * duration
                    seg_data['log_raw_duration'] = np.log1p(raw_duration)
                    seg_data['duration_ratio'] = raw_duration / duration if duration > 0 else 1.0

                    # Deduplicate: skip if this exact metadata already seen
                    key = tuple(sorted(seg_data.items()))
                    if key in seen:
                        num_dupes += 1
                        continue
                    seen.add(key)

                    segments.append(seg_data)
            except Exception as e:
                print(f"Error loading {file}: {e}")

    print(f"Skipped {num_dupes} duplicate segments")
    return pd.DataFrame(segments)

def log_seed_data(seeds_df, seed_type, label_desc):
    """Log comprehensive data for seed segments."""
    if len(seeds_df) == 0:
        return

    print(f"\n{seed_type} seeds ({label_desc}) - {len(seeds_df)} total:")
    for i, (_, seg) in enumerate(seeds_df.head(10).iterrows(), 1):
        print(f"  {i:3d}. SPS={seg['sps']:.2f}, Raw_SPS={seg['raw_sps']:.2f}, "
              f"logprob={seg['avg_logprob']:.3f}, no_speech={seg['no_speech_prob']:.3f}, "
              f"compression={seg['compression_ratio']:.2f}, duration={seg['duration_sanity']:.2f}s, "
              f"raw_duration={seg['raw_duration']:.2f}s")
        print(f"       Text: '{seg['text']}'")
        print()

    # Show statistics
    print(f"\n{seed_type} seed statistics:")
    for metric, col in [('SPS', 'sps'), ('Logprob', 'avg_logprob'), ('Compression', 'compression_ratio')]:
        data = seeds_df[col]
        print(f"  {metric}: mean={data.mean():.3f}, std={data.std():.3f}, min={data.min():.3f}, max={data.max():.3f}")

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
        ((df['avg_logprob'] < -0.85)          # This low of a logprob is almost always a hallucination
        | (df['compression_ratio'] > 2.3)    # High compressibility is usually a hallucination
        | (df['sps'] > 9))                    # No one speaks this fast
        & df['text'].str.contains("Thank you", na=False)  # Hack. Nothing good enough to
    )

    # Conservative negative seeds (likely valid)
    h_neg = (
        (df['avg_logprob'] > -0.5)          # solid confidence drop
        & (df['compression_ratio'] < 1.2)
        & (df['sps'] < 9)
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

    # Log all seed data
    pos_seeds = df[df['seed_label'] == 1]
    neg_seeds = df[df['seed_label'] == 0]

    log_seed_data(pos_seeds, "Positive", "likely hallucinations")
    log_seed_data(neg_seeds, "Negative", "likely valid")

    # Define features (trimmed to remove redundant transformations)
    features = [
        'avg_logprob',
        'no_speech_prob',
        'compression_ratio',
        'log_duration',
        'log_sps',
        'log_raw_duration',
        'log_raw_sps',
        'duration_ratio',
        'logprob_duration_interaction'
    ]

    X = df[features].values

    # Step 2: Train kNN on seed labels
    print("\nTraining k-NN classifier on seed labels...")

    labeled_mask = df['seed_label'].notna()
    X_seed = X[labeled_mask]
    y_seed = df.loc[labeled_mask, 'seed_label'].values.astype(int)

    # Auto-select k based on seed data size
    n_seed_samples = len(X_seed)
    optimal_k = min(max(int(np.sqrt(n_seed_samples)), 3), n_seed_samples // 2)
    print(f"Using k={optimal_k} neighbors (from {n_seed_samples} seed samples)")

    # Create pipeline with scaling (important for kNN)
    knn_pipeline = Pipeline([
        ('scale', StandardScaler()),
        ('knn', KNeighborsClassifier(
            n_neighbors=optimal_k,
            weights='distance'       # closer neighbors weigh more
        ))
    ])

    # --- step 2: train k-NN on seeds -------------------------------
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # out-of-fold probas for the seeds
    seed_scores = cross_val_predict(
        knn_pipeline,                # pipeline defined earlier
        X_seed, y_seed,
        cv=cv,
        method="predict_proba"
    )[:, 1]

    # store the scores for thresholding
    df.loc[labeled_mask, 'knn_score'] = seed_scores

    # finally fit on the full seed set before scoring the rest
    knn_pipeline.fit(X_seed, y_seed)
    df.loc[~labeled_mask, 'knn_score'] = knn_pipeline.predict_proba(
        X[~labeled_mask])[:, 1]

    # --- step 2 done: kNN scores are in df['knn_score'] ---------------------

    # Debug: how are the scores distributed?
    for lbl, mask in {
        "Positive seeds":  df['seed_label'] == 1,
        "Negative seeds":  df['seed_label'] == 0,
        "Un-labelled":     df['seed_label'].isna()
    }.items():
        scores = df.loc[mask, 'knn_score']
        if scores.empty:
            continue
        print(f"{lbl:15s} | n={len(scores):4d}  min={scores.min():.3f}  "
              f"25%={scores.quantile(.25):.3f}  median={scores.median():.3f}  "
              f"75%={scores.quantile(.75):.3f}  max={scores.max():.3f}")
    print()  # blank line for readability

    # Step 3: derive a threshold from the seed scores
    print("Applying threshold to segment scores...")

    neg_seed_scores = df.loc[df['seed_label'] == 0, 'knn_score']
    pos_seed_scores = df.loc[df['seed_label'] == 1, 'knn_score']

    max_neg = neg_seed_scores.max()
    min_pos = pos_seed_scores.min()

    if min_pos > max_neg:
        # clear separation – use the midpoint
        threshold = (max_neg + min_pos) / 2
        reason = "mid-point between max-neg and min-pos"
    else:
        # fallback to percentile rule, but ensure it’s >0
        threshold = np.percentile(neg_seed_scores, 95)
        if threshold <= 0:
            threshold = 1e-3
        reason = "95th percentile of negative seeds"

    print(f"\nChosen threshold: {threshold:.3f}  ({reason})")

    df['is_hallucination'] = (df['knn_score'] >= threshold).astype(int)

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
    print(f"\nExample detected hallucinations:")
    for _, seg in hallucination_examples.iterrows():
        print(f"  Score={seg['knn_score']:.3f}, text='{seg['text']}'")

    non_hallucination_examples = df[df['is_hallucination'] == 0].head(10)
    print(f"\nExample detected non-hallucinations:")
    for _, seg in non_hallucination_examples.iterrows():
        print(f"  Score={seg['knn_score']:.3f}, text='{seg['text']}'")

    # --- after training the GB model ---
    gb_scores = model.predict_proba(X_final)[:, 1]

    # choose threshold on GB scores, e.g. same 95-percentile rule
    neg_scores = gb_scores[df['seed_label'] == 0]
    threshold = np.percentile(neg_scores, 95)
    print(f"\nPost-training threshold: {threshold:.3f}")

    # Save model
    model_dir = Path("Models")
    model_dir.mkdir(exist_ok=True)

    model_bundle = {
        "model": model,
        "threshold": threshold,
        "features": features,
    }

    output_path = model_dir / "thankyou_filter_gb.pkl"
    joblib.dump(model_bundle, output_path)
    print(f"\nModel saved to: {output_path}")

if __name__ == "__main__":
    main()
