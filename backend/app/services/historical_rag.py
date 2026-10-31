
import json
from pathlib import Path
from functools import lru_cache

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[2]

INDEX_DIR = BASE_DIR / "data" / "index"

MODEL_NAME = "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=1)
def get_model():

    return SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )


@lru_cache(maxsize=1)
def get_index():

    path = INDEX_DIR / "historical.faiss"

    if not path.exists():

        raise FileNotFoundError(
            "Historical index not found. "
            "Run python -m scripts.build_historical_index"
        )

    return faiss.read_index(str(path))


@lru_cache(maxsize=1)
def get_metadata():

    path = INDEX_DIR / "historical_metadata.json"

    with open(path, "r", encoding="utf-8") as file:

        return json.load(file)


def retrieve_history(query, top_k=3):

    model = get_model()

    index = get_index()

    metadata = get_metadata()

    embedding = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    embedding = np.asarray(
        embedding,
        dtype="float32"
    )

    scores, indices = index.search(
        embedding,
        top_k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx < 0:
            continue

        record = metadata[idx].copy()

        record["similarity"] = round(
            float(score), 4
        )

        results.append(record)

    return results
