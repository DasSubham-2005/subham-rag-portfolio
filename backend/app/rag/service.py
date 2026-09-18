# 

from pathlib import Path
import os
import threading

# ============================================================
# Render / low-memory optimizations
# ============================================================

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Limit native CPU thread usage
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import torch

# Keep PyTorch from creating many CPU threads
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

import chromadb
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)

from app.core.config import settings


# ============================================================
# Paths
# ============================================================

ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# Lazy-loaded RAG resources
# ============================================================

client = None
embedder = None
collection = None

# Prevent two requests from loading the embedding model twice
_init_lock = threading.Lock()


# ============================================================
# Chroma + embedding model
# ============================================================

def get_collection():
    global client, embedder, collection

    if collection is not None:
        return collection

    with _init_lock:

        # Another request may have initialized it
        if collection is not None:
            return collection

        print("RAG: starting Chroma initialization", flush=True)

        # ----------------------------------------------------
        # Chroma client
        # ----------------------------------------------------

        client = chromadb.PersistentClient(
            path=str(ROOT / settings.chroma_dir)
        )

        print("RAG: Chroma client ready", flush=True)

        # ----------------------------------------------------
        # all-MiniLM-L6-v2
        #
        # Keep the required embedding model.
        # CPU-only + single-threaded for Render memory/CPU.
        # ----------------------------------------------------

        embedder = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2",
            device="cpu",
            normalize_embeddings=True,
        )

        print("RAG: embedding model ready", flush=True)

        # ----------------------------------------------------
        # Chroma collection
        # ----------------------------------------------------

        collection = client.get_or_create_collection(
            name="portfolio_knowledge",
            embedding_function=embedder,
        )

        print("RAG: collection ready", flush=True)

    return collection


# ============================================================
# Text chunking
# ============================================================

def chunk_text(
    text: str,
    size: int = 700,
    overlap: int = 100,
):
    words = text.split()

    chunks = []
    start = 0

    step = max(1, size - overlap)

    while start < len(words):
        chunk = " ".join(words[start:start + size])

        if chunk.strip():
            chunks.append(chunk)

        start += step

    return chunks


# ============================================================
# Index documents
# ============================================================

def index_documents(documents: list[dict]):
    collection = get_collection()

    ids = []
    texts = []
    metas = []

    for doc in documents:

        chunks = chunk_text(doc["text"])

        for i, chunk in enumerate(chunks):

            ids.append(
                f"{doc['id']}-{i}"
            )

            texts.append(chunk)

            metas.append(
                {
                    "source": doc["source"]
                }
            )

    if ids:

        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metas,
        )

    return len(ids)


# ============================================================
# Retrieve relevant portfolio knowledge
# ============================================================

def retrieve(
    query: str,
    k: int = 5,
):
    collection = get_collection()

    query_lower = query.lower()

    source_hint = None

    # --------------------------------------------------------
    # Experience
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
    # Education
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
    # Skills
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
    # Projects
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
    # Certificates
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

    # ========================================================
    # Project-specific retrieval
    # ========================================================

    if source_hint == "projects":

        all_data = collection.get(
            include=[
                "documents",
                "metadatas",
            ]
        )

        project_docs = []

        for doc, meta in zip(
            all_data.get("documents", []),
            all_data.get("metadatas", []),
        ):

            source = (meta or {}).get(
                "source",
                "",
            )

            if source.startswith("project:"):

                project_docs.append(
                    {
                        "text": doc,
                        "source": source,
                    }
                )

        return project_docs[:k]

    # ========================================================
    # Skills-specific retrieval
    # ========================================================

    if source_hint == "skills":

        all_data = collection.get(
            include=[
                "documents",
                "metadatas",
            ]
        )

        skill_docs = []

        for doc, meta in zip(
            all_data.get("documents", []),
            all_data.get("metadatas", []),
        ):

            source = (meta or {}).get(
                "source",
                "",
            )

            if source == "skills":

                skill_docs.append(
                    {
                        "text": doc,
                        "source": source,
                    }
                )

        return skill_docs

    # ========================================================
    # Source-filtered semantic retrieval
    # ========================================================

    if source_hint:

        result = collection.query(
            query_texts=[query],
            n_results=k,
            where={
                "source": source_hint
            },
        )

    else:

        result = collection.query(
            query_texts=[query],
            n_results=k,
        )

    docs = result.get(
        "documents",
        [[]],
    )[0]

    metas = result.get(
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
            docs,
            metas,
        )
    ]