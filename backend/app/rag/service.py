from pathlib import Path
import os
import re
import threading
import hashlib
import numpy as np

os.environ["ANONYMIZED_TELEMETRY"] = "False"

from app.core.config import settings


ROOT = Path(__file__).resolve().parents[2]

client = None
collection = None

_init_lock = threading.Lock()
_rebuild_lock = threading.Lock()

EMBEDDING_DIMENSION = 768


# ============================================================
# CHROMA
# ============================================================

def get_collection():
    global client, collection

    if collection is not None:
        return collection

    with _init_lock:
        if collection is not None:
            return collection

        print(
            "RAG: starting Chroma initialization",
            flush=True,
        )

        import chromadb

        client = chromadb.PersistentClient(
            path=str(ROOT / settings.chroma_dir)
        )

        print(
            "RAG: Chroma client ready",
            flush=True,
        )

        collection = client.get_or_create_collection(
            name="portfolio_knowledge_v2"
        )

        print(
            f"RAG: collection ready ({collection.count()} chunks)",
            flush=True,
        )

    return collection


# ============================================================
# LIGHTWEIGHT LOCAL EMBEDDINGS
# ============================================================

def local_embed(texts: list[str]):
    """
    Lightweight local text embeddings.

    No Gemini API.
    No external embedding service.
    No ML model.
    No extra package.

    Uses hashed word features with cosine normalization.
    """

    embeddings = []

    for text in texts:

        vector = np.zeros(
            EMBEDDING_DIMENSION,
            dtype=np.float32,
        )

        words = re.findall(
            r"\b[a-zA-Z0-9+#.-]+\b",
            text.lower(),
        )

        for word in words:

            digest = hashlib.md5(
                word.encode("utf-8")
            ).digest()

            index = int.from_bytes(
                digest[:4],
                "little",
            ) % EMBEDDING_DIMENSION

            vector[index] += 1.0

        # Normalize for cosine similarity.
        norm = np.linalg.norm(vector)

        if norm > 0:
            vector = vector / norm

        embeddings.append(
            vector.tolist()
        )

    return embeddings


def embed_documents(texts: list[str]):
    return local_embed(texts)


def embed_query(text: str):
    return local_embed([text])[0]


# ============================================================
# TEXT CHUNKING
# ============================================================

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
        size - overlap,
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


# ============================================================
# INDEX DOCUMENTS
# ============================================================

def index_documents(
    documents: list[dict],
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
        f"RAG: generating {len(texts)} local embeddings...",
        flush=True,
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
        flush=True,
    )

    return len(ids)


# ============================================================
# AUTOMATIC REBUILD
# ============================================================

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

            from app.db.session import SessionLocal
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


# ============================================================
# GET DOCUMENTS BY SOURCE
# ============================================================

def get_all_source_documents(
    source_prefix: str,
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
            "",
        )

        if source.startswith(
            source_prefix
        ):

            results.append({
                "text": document,
                "source": source,
            })

    return results


# ============================================================
# RETRIEVAL
# ============================================================

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


    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # CERTIFICATES
    # --------------------------------------------------------

    elif any(
        word in query_lower
        for word in [
            "certificate",
            "certification",
            "certifications",
        ]
    ):

        source_hint = "certificates"


    # --------------------------------------------------------
    # PROJECT QUERIES
    # --------------------------------------------------------

    if source_hint == "projects":

        results = get_all_source_documents(
            "project:"
        )

        return results[:k]


    # --------------------------------------------------------
    # SKILLS QUERIES
    # --------------------------------------------------------

    if source_hint == "skills":

        return get_all_source_documents(
            "skills"
        )


    # --------------------------------------------------------
    # SEMANTIC RETRIEVAL
    # --------------------------------------------------------

    query_embedding = embed_query(
        query
    )

    n_results = min(
        k,
        collection.count(),
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
        [[]],
    )[0]

    metadatas = result.get(
        "metadatas",
        [[]],
    )[0]


    return [
        {
            "text": document,
            "source": (
                metadata or {}
            ).get(
                "source",
                "portfolio",
            ),
        }

        for document, metadata in zip(
            documents,
            metadatas,
        )
    ]