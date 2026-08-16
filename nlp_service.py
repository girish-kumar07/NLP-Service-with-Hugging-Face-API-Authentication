"""
nlp_service.py
Wraps the Hugging Face Inference API for Named Entity Recognition, Language
Detection, and Sentiment Analysis, with error handling for network/API failures.
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

BASE_URL = "https://router.huggingface.co/hf-inference/models"

# Multiple candidate models per task, tried in order. Hugging Face's free
# Inference Providers periodically change which models they serve, so we
# fall back to the next candidate if one returns "not supported".
SENTIMENT_MODELS = [
    # Emotion-detection models (joy, sadness, anger, fear, surprise, disgust, neutral) - tried first
    "j-hartmann/emotion-english-distilroberta-base",
    "SamLowe/roberta-base-go_emotions",
    "j-hartmann/emotion-english-roberta-large",
    # Binary POSITIVE/NEGATIVE fallbacks if emotion models are unavailable
    "distilbert-base-uncased-finetuned-sst-2-english",
    "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "ProsusAI/finbert",
]
NER_MODELS = [
    "dslim/bert-base-NER",
    "dbmdz/bert-large-cased-finetuned-conll03-english",
    "StanfordAIMI/stanford-deidentifier-base",
]
LANGUAGE_MODELS = [
    "papluca/xlm-roberta-base-language-detection",
]


class NLPServiceError(Exception):
    """Raised when an NLP API call fails for any reason."""
    pass


class ModelNotSupportedError(NLPServiceError):
    """Raised specifically when a model isn't served by the provider (HTTP 400
    'not supported'), so callers can try the next fallback model."""
    pass


class NLPService:
    def __init__(self):
        if not HF_API_TOKEN or HF_API_TOKEN == "paste_your_real_huggingface_token_here":
            raise NLPServiceError(
                "HF_API_TOKEN is not set. Please add your real token to the .env file."
            )
        self._headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    def _query(self, model: str, payload: dict, max_retries: int = 3):
        """
        Sends a request to the Hugging Face Inference API.
        Retries if the model is still loading (HF returns 503 with 'estimated_time').
        """
        url = f"{BASE_URL}/{model}"

        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=self._headers, json=payload, timeout=30)
            except requests.exceptions.RequestException as e:
                raise NLPServiceError(f"Network error while calling Hugging Face API: {e}")

            if response.status_code == 200:
                return response.json()

            if response.status_code == 503:
                # Model is loading on Hugging Face's servers - wait and retry
                try:
                    wait_time = response.json().get("estimated_time", 5)
                except ValueError:
                    wait_time = 5
                time.sleep(min(wait_time, 15))
                continue

            if response.status_code == 401:
                raise NLPServiceError(
                    "Invalid Hugging Face API token. Please check your .env file."
                )

            if response.status_code == 400 and "not supported" in response.text.lower():
                raise ModelNotSupportedError(
                    f"Model '{model}' is not supported by the current provider."
                )

            raise NLPServiceError(
                f"Hugging Face API returned an error (status {response.status_code}): {response.text}"
            )

        raise NLPServiceError("Model is still loading after multiple retries. Please try again shortly.")

    def analyze_sentiment(self, text: str) -> str:
        """Returns the top predicted sentiment label for the given text.
        Tries each candidate model in order until one succeeds."""
        if not text or not text.strip():
            raise NLPServiceError("Input text cannot be empty.")

        last_error = None
        for model in SENTIMENT_MODELS:
            try:
                result = self._query(model, {"inputs": text})
                scored_labels = result[0]
                top = max(scored_labels, key=lambda x: x["score"])
                return top["label"]
            except ModelNotSupportedError as e:
                last_error = e
                continue
            except (KeyError, IndexError, TypeError):
                last_error = NLPServiceError(f"Unexpected response format from model '{model}'.")
                continue

        raise NLPServiceError(f"All sentiment models failed. Last error: {last_error}")

    def extract_entities(self, text: str):
        """Returns a list of (entity_text, entity_type) tuples.
        Tries each candidate model in order until one succeeds."""
        if not text or not text.strip():
            raise NLPServiceError("Input text cannot be empty.")

        last_error = None
        for model in NER_MODELS:
            try:
                result = self._query(
                    model, {"inputs": text, "parameters": {"aggregation_strategy": "simple"}}
                )
                return [(e["word"], e["entity_group"]) for e in result]
            except ModelNotSupportedError as e:
                last_error = e
                continue
            except (KeyError, TypeError):
                last_error = NLPServiceError(f"Unexpected response format from model '{model}'.")
                continue

        raise NLPServiceError(f"All NER models failed. Last error: {last_error}")

    def detect_language(self, text: str) -> str:
        """Returns the most likely detected language code.
        Tries each candidate model in order until one succeeds."""
        if not text or not text.strip():
            raise NLPServiceError("Input text cannot be empty.")

        last_error = None
        for model in LANGUAGE_MODELS:
            try:
                result = self._query(model, {"inputs": text})
                scored_labels = result[0]
                top = max(scored_labels, key=lambda x: x["score"])
                return top["label"]
            except ModelNotSupportedError as e:
                last_error = e
                continue
            except (KeyError, IndexError, TypeError):
                last_error = NLPServiceError(f"Unexpected response format from model '{model}'.")
                continue

        raise NLPServiceError(f"All language detection models failed. Last error: {last_error}")