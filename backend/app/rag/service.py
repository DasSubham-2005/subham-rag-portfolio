from pathlib import Path
import os
import threading

# ============================================================
# Environment / low-memory settings
# ============================================================

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from app.core.config import settings


# ============================================================
# Paths
# ============================================================

ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# Lazy-loaded RAG resources
# ============================================================

client = None
model = None
collection = None

_init_lock = threading.Lock()


# ============================================================
# RAG initialization
# ============================================================

def get_collection():
    """
    Lazily initialize ChromaDB and all-MiniLM-L6-v2.

    Heavy libraries are imported only when the first RAG
    request actually needs them.
    """

    global client, model, collection

    if collection is not None:
        return collection

    with _init_lock:

        if collection is not None:
            return collection

        print("RAG: starting Chroma initialization", flush=True)

        # Heavy imports happen only when RAG is requested
        import torch
        import chromadb
        from sentence_transformers import SentenceTransformer

        # Keep PyTorch CPU usage lightweight
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)

        # ----------------------------------------------------
        # Chroma
        # ----------------------------------------------------

        client = chromadb.PersistentClient(
            path=str(ROOT / settings.chroma_dir)
        )

        print("RAG: Chroma client ready", flush=True)

        # ----------------------------------------------------
        # all-MiniLM-L6-v2
        # ----------------------------------------------------

        model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device="cpu",
        )

        model.eval()

        print("RAG: embedding model ready", flush=True)

        # ----------------------------------------------------
        # Chroma collection
        #
        # Embeddings are generated manually so Chroma does not
        # create another embedding model internally.
        # ----------------------------------------------------

        collection = client.get_or_create_collection(
            name="portfolio_knowledge"
        )

        print("RAG: collection ready", flush=True)

    return collection


# ============================================================
# Embedding generation
# ============================================================

def embed_texts(texts: list[str]):
    """
    Generate semantic embeddings using all-MiniLM-L6-v2.
    """

    get_collection()

    import torch

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
# Text chunking
# ============================================================

def chunk_text(
    text: str,
    size: int = 700,
    overlap: int = 100,
):
    """
    Split portfolio text into overlapping word chunks.
    """

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
    """
    Convert documents into chunks, generate embeddings,
    and store them in ChromaDB.
    """

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

            metadatas.append(
                {
                    "source": document["source"]
                }
            )

    if not texts:
        return 0

    embeddings = embed_texts(texts)

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(ids)


# ============================================================
# Retrieve portfolio knowledge
# ============================================================

def retrieve(
    query: str,
    k: int = 5,
):
    """
    Retrieve the most relevant portfolio knowledge
    using semantic embeddings.
    """

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
    # Project retrieval
    # ========================================================

    if source_hint == "projects":

        all_data = collection.get(
            include=[
                "documents",
                "metadatas",
            ]
        )

        project_documents = []

        for document, metadata in zip(
            all_data.get("documents", []),
            all_data.get("metadatas", []),
        ):

            source = (
                metadata or {}
            ).get(
                "source",
                "",
            )

            if source.startswith("project:"):

                project_documents.append(
                    {
                        "text": document,
                        "source": source,
                    }
                )

        return project_documents[:k]

    # ========================================================
    # Skills retrieval
    # ========================================================

    if source_hint == "skills":

        all_data = collection.get(
            include=[
                "documents",
                "metadatas",
            ]
        )

        skill_documents = []

        for document, metadata in zip(
            all_data.get("documents", []),
            all_data.get("metadatas", []),
        ):

            source = (
                metadata or {}
            ).get(
                "source",
                "",
            )

            if source == "skills":

                skill_documents.append(
                    {
                        "text": document,
                        "source": source,
                    }
                )

        return skill_documents

    # ========================================================
    # Semantic query
    # ========================================================

    query_embedding = embed_texts(
        [query]
    )[0]

    # --------------------------------------------------------
    # Filtered semantic retrieval
    # --------------------------------------------------------

    if source_hint:

        result = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=k,
            where={
                "source": source_hint
            },
        )

    # --------------------------------------------------------
    # General semantic retrieval
    # --------------------------------------------------------

    else:

        result = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=k,
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