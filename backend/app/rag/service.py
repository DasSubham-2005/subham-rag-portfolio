from pathlib import Path
import os
import threading

# ============================================================
# Low-memory / Render optimizations
# ============================================================

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import torch

torch.set_num_threads(1)
torch.set_num_interop_threads(1)

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import settings


# ============================================================
# Globals
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

client = None
model = None
collection = None

_init_lock = threading.Lock()


# ============================================================
# Initialize Chroma + all-MiniLM-L6-v2
# ============================================================

def get_collection():
    global client, model, collection

    if collection is not None:
        return collection

    with _init_lock:

        if collection is not None:
            return collection

        print("RAG: starting Chroma initialization", flush=True)

        client = chromadb.PersistentClient(
            path=str(ROOT / settings.chroma_dir)
        )

        print("RAG: Chroma client ready", flush=True)

        # Direct SentenceTransformer loading
        model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device="cpu",
        )

        model.eval()

        print("RAG: embedding model ready", flush=True)

        collection = client.get_or_create_collection(
            name="portfolio_knowledge"
        )

        print("RAG: collection ready", flush=True)

    return collection


# ============================================================
# Generate embeddings
# ============================================================

def embed_texts(texts: list[str]):
    get_collection()

    with torch.inference_mode():
        embeddings = model.encode(
            texts,
            batch_size=1,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

    return embeddings.tolist()


# ============================================================
# Chunk text
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

        chunk = " ".join(
            words[start:start + size]
        )

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

    if not texts:
        return 0

    embeddings = embed_texts(texts)

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metas,
    )

    return len(ids)


# ============================================================
# Retrieve relevant knowledge
# ============================================================

def retrieve(
    query: str,
    k: int = 5,
):
    collection = get_collection()

    query_lower = query.lower()

    source_hint = None

    # Experience
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

    # Education
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

    # Skills
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

    # Projects
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

    # Certificates
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
    # Projects
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
    # Skills
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
    # Semantic retrieval
    # ========================================================

    query_embedding = embed_texts(
        [query]
    )[0]

    if source_hint:

        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where={
                "source": source_hint
            },
        )

    else:

        result = collection.query(
            query_embeddings=[query_embedding],
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