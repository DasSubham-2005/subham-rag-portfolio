from pathlib import Path
import os
import threading
import requests
import numpy as np

os.environ["ANONYMIZED_TELEMETRY"] = "False"

from app.core.config import settings

ROOT = Path(__file__).resolve().parents[2]

client = None
collection = None

_init_lock = threading.Lock()
_rebuild_lock = threading.Lock()

GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768


def get_collection():
    global client, collection

    if collection is not None:
        return collection

    with _init_lock:
        if collection is not None:
            return collection

        print("RAG: starting Chroma initialization", flush=True)

        import chromadb

        client = chromadb.PersistentClient(
            path=str(ROOT / settings.chroma_dir)
        )

        print("RAG: Chroma client ready", flush=True)

        collection = client.get_or_create_collection(
            name="portfolio_knowledge_v2"
        )

        print(
            f"RAG: collection ready ({collection.count()} chunks)",
            flush=True
        )

    return collection


def gemini_embed(texts: list[str], task_type: str):
    """
    Generate embeddings using Gemini API.

    No local embedding model is loaded.
    This keeps RAM usage low for 512MB hosting.
    """

    api_key = getattr(settings, "gemini_api_key", "")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-embedding-001:embedContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    embeddings = []

    for text in texts:

        payload = {
            "model": "models/gemini-embedding-001",
            "content": {
                "parts": [
                    {
                        "text": text
                    }
                ]
            },
            "taskType": task_type,
            "outputDimensionality": EMBEDDING_DIMENSION,
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if not response.ok:
            raise RuntimeError(
                f"Gemini embedding API error "
                f"{response.status_code}: {response.text}"
            )

        data = response.json()

        values = (
            data.get("embedding", {})
            .get("values")
        )

        if not values:
            raise RuntimeError(
                "Gemini returned an empty embedding."
            )

        # Normalize for cosine similarity.
        vector = np.asarray(
            values,
            dtype=np.float32
        )

        norm = np.linalg.norm(vector)

        if norm > 0:
            vector = vector / norm

        embeddings.append(
            vector.tolist()
        )

    return embeddings


def embed_documents(texts: list[str]):
    return gemini_embed(
        texts,
        "RETRIEVAL_DOCUMENT"
    )


def embed_query(text: str):
    return gemini_embed(
        [text],
        "RETRIEVAL_QUERY"
    )[0]


def chunk_text(
    text: str,
    size: int = 500,
    overlap: int = 50,
):
    words = text.split()

    chunks = []

    start = 0

    step = max(
        1,
        size - overlap
    )

    while start < len(words):

        chunk = " ".join(
            words[
                start:start + size
            ]
        )

        if chunk.strip():
            chunks.append(chunk)

        start += step

    return chunks


def index_documents(
    documents: list[dict]
):
    collection = get_collection()

    ids = []
    texts = []
    metadatas = []

    for document in documents:

        chunks = chunk_text(
            document["text"]
        )

        for index, chunk in enumerate(chunks):

            ids.append(
                f"{document['id']}-{index}"
            )

            texts.append(chunk)

            metadatas.append({
                "source": document["source"]
            })

    if not texts:
        return 0

    print(
        f"RAG: generating {len(texts)} embeddings...",
        flush=True
    )

    embeddings = embed_documents(
        texts
    )

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(
        f"RAG: indexed {len(ids)} chunks",
        flush=True
    )

    return len(ids)


def auto_rebuild_if_empty():

    collection = get_collection()

    if collection.count() > 0:
        return

    with _rebuild_lock:

        if collection.count() > 0:
            return

        print(
            "RAG: collection empty. "
            "Starting automatic rebuild...",
            flush=True,
        )

        try:

            from app.core.database import SessionLocal
            from app.rag.ingest import build_documents

            db = SessionLocal()

            try:

                documents = build_documents(
                    db
                )

                if not documents:
                    print(
                        "RAG: no portfolio data found.",
                        flush=True,
                    )
                    return

                count = index_documents(
                    documents
                )

                print(
                    f"RAG: automatic rebuild "
                    f"completed ({count} chunks)",
                    flush=True,
                )

            finally:
                db.close()

        except Exception as e:

            print(
                f"RAG: automatic rebuild failed: {e}",
                flush=True,
            )


def get_all_source_documents(
    source_prefix: str
):
    collection = get_collection()

    data = collection.get(
        include=[
            "documents",
            "metadatas",
        ]
    )

    results = []

    for document, metadata in zip(
        data.get("documents", []),
        data.get("metadatas", []),
    ):

        source = (
            metadata or {}
        ).get(
            "source",
            ""
        )

        if source.startswith(
            source_prefix
        ):
            results.append({
                "text": document,
                "source": source,
            })

    return results


def retrieve(
    query: str,
    k: int = 5,
):

    collection = get_collection()

    # Automatically restore RAG if empty.
    if collection.count() == 0:
        auto_rebuild_if_empty()

    if collection.count() == 0:
        return []

    query_lower = query.lower()

    source_hint = None

    if any(
        word in query_lower
        for word in [
            "experience",
            "work experience",
            "internship",
            "job",
            "role",
            "worked",
            "career",
        ]
    ):
        source_hint = "experience"

    elif any(
        word in query_lower
        for word in [
            "education",
            "degree",
            "college",
            "university",
            "school",
            "study",
            "studied",
        ]
    ):
        source_hint = "education"

    elif any(
        word in query_lower
        for word in [
            "skill",
            "skills",
            "technology",
            "technologies",
            "programming",
        ]
    ):
        source_hint = "skills"

    elif any(
        word in query_lower
        for word in [
            "project",
            "projects",
            "built",
            "developed",
        ]
    ):
        source_hint = "projects"

    elif any(
        word in query_lower
        for word in [
            "certificate",
            "certification",
            "certifications",
        ]
    ):
        source_hint = "certificates"

    # Project queries
    if source_hint == "projects":

        results = get_all_source_documents(
            "project:"
        )

        return results[:k]

    # Skills queries
    if source_hint == "skills":

        return get_all_source_documents(
            "skills"
        )

    # Normal semantic retrieval
    query_embedding = embed_query(
        query
    )

    n_results = min(
        k,
        collection.count()
    )

    if source_hint:

        result = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=n_results,
            where={
                "source": source_hint
            },
        )

    else:

        result = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=n_results,
        )

    documents = result.get(
        "documents",
        [[]]
    )[0]

    metadatas = result.get(
        "metadatas",
        [[]]
    )[0]

    return [
        {
            "text": document,
            "source": (
                metadata or {}
            ).get(
                "source",
                "portfolio"
            ),
        }
        for document, metadata in zip(
            documents,
            metadatas,
        )
    ]