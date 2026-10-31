
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "historical_cricket.json"
INDEX_DIR = BASE_DIR / "data" / "index"

INDEX_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "BAAI/bge-small-en-v1.5"


def build_index():

    with open(DATA_PATH, "r", encoding="utf-8") as file:
        records = json.load(file)

    documents = []

    for record in records:

        text = f"""
        Category: {record['category']}
        Title: {record['title']}
        Content: {record['content']}
        Entities: {', '.join(record['entities'])}
        """

        documents.append(text.strip())

    print("Loading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    embeddings = model.encode(
        documents,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    index = faiss.IndexFlatIP(
        embeddings.shape[1]
    )

    index.add(embeddings)

    faiss.write_index(
        index,
        str(INDEX_DIR / "historical.faiss")
    )

    with open(
        INDEX_DIR / "historical_metadata.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("Historical cricket index created.")
    print("Total records:", index.ntotal)


if __name__ == "__main__":
    build_index()
