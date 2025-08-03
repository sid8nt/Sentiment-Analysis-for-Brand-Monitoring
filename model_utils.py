import pandas as pd
import pickle
import os
import re

# Define example neutral keywords
neutral_keywords = [
    "ok", "okay", "average", "not bad", "fine", "decent", "fair", "so-so",
    "nothing special", "mediocre", "acceptable", "ordinary", "not great", "not good"
]

def is_neutral(review: str):
    review = review.lower()
    return any(re.search(rf"\b{re.escape(word)}\b", review) for word in neutral_keywords)

def run_model(df: pd.DataFrame, model_choice: str = 'random_forest'):
    if 'review' not in df.columns:
        raise ValueError("DataFrame must contain a 'review' column.")

    if model_choice != 'random_forest':
        raise ValueError("Only 'random_forest' model is supported currently.")

    reviews = df['review'].astype(str).tolist()

    base_path = os.path.dirname(os.path.abspath(__file__))
    vectorizer_path = os.path.join(base_path, 'models', 'vectorizer.pkl')
    model_path = os.path.join(base_path, 'models', 'random_forest_model.pkl')

    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    X = vectorizer.transform(reviews)
    preds = model.predict(X)

    sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}

    results = []
    for review, pred in zip(reviews, preds):
        if is_neutral(review):
            sentiment = 'Neutral'
        elif pred == 1:
            sentiment = 'Positive'
        elif pred == 0:
            sentiment = 'Negative'
        else:
            sentiment = 'Unknown'

        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

        results.append({'review': review, 'sentiment': sentiment})

    return results, sentiment_counts


def calculate_percentages(counts):
    total = sum(counts.values())
    if total == 0:
        return {k: 0 for k in counts}
    return {k: round(v / total * 100, 2) for k, v in counts.items()}
