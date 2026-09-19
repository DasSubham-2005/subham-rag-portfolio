from pathlib import Path
import os
import threading

# Keep runtime lightweight
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from app.core.config import settings

ROOT = Path(__file__).resolve().parents[2]

client = None
model = None
tokenizer = None
collection = None

_init_lock = threading.Lock()


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_collection():
    global client, model, tokenizer, collection

    if collection is not None:
        return collection

    with _init_lock:
        if collection is not None:
            return collection

        print("RAG: starting Chroma initialization", flush=True)

        # --------------------------------
        # STEP 1: Import torch
        # --------------------------------
        print("RAG: importing torch", flush=True)

        import torch

        print("RAG: torch imported", flush=True)

        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)

        # --------------------------------
        # STEP 2: Import ChromaDB
        # --------------------------------
        print("RAG: importing chromadb", flush=True)

        import chromadb

        print("RAG: chromadb imported", flush=True)

        # --------------------------------
        # STEP 3: Import Transformers
        # --------------------------------
        print("RAG: importing transformers", flush=True)

        from transformers import AutoTokenizer, AutoModel

        print("RAG: transformers imported", flush=True)

        # --------------------------------
        # STEP 4: Create Chroma client
        # --------------------------------
        print("RAG: creating Chroma client", flush=True)

        client = chromadb.PersistentClient(
            path=str(ROOT / settings.chroma_dir)
        )

        print("RAG: Chroma client ready", flush=True)

        # --------------------------------
        # STEP 5: Load MiniLM tokenizer
        # --------------------------------
        print("RAG: loading MiniLM tokenizer", flush=True)

        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        print("RAG: tokenizer ready", flush=True)

        # --------------------------------
        # STEP 6: Load MiniLM model
        # --------------------------------
        print("RAG: loading all-MiniLM-L6-v2", flush=True)

        model = AutoModel.from_pretrained(
            MODEL_NAME
        )

        model.to("cpu")
        model.eval()

        print("RAG: embedding model ready", flush=True)

        # --------------------------------
        # STEP 7: Create Chroma collection
        # --------------------------------
        print("RAG: creating collection", flush=True)

        collection = client.get_or_create_collection(
            name="portfolio_knowledge"
        )

        print("RAG: collection ready", flush=True)

    return collection


def embed_texts(texts: list[str]):
    get_collection()

    import torch
    import torch.nn.functional as F

    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors="pt",
    )

    with torch.inference_mode():
        output = model(**encoded)

        token_embeddings = output.last_hidden_state
        attention_mask = encoded["attention_mask"]

        mask = attention_mask.unsqueeze(-1).expand(
            token_embeddings.size()
        ).float()

        masked_embeddings = token_embeddings * mask

        summed = masked_embeddings.sum(dim=1)

        counts = mask.sum(dim=1).clamp(min=1e-9)

        embeddings = summed / counts

        embeddings = F.normalize(
            embeddings,
            p=2,
            dim=1,
        )

    return embeddings.cpu().numpy().tolist()


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


def index_documents(documents: list[dict]):
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

    embeddings = embed_texts(texts)

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(ids)


def retrieve(
    query: str,
    k: int = 5,
):
    collection = get_collection()

    query_lower = query.lower()
    source_hint = None

    # --------------------------------
    # Detect portfolio category
    # --------------------------------

    if any(word in query_lower for word in [
        "experience",
        "work experience",
        "internship",
        "job",
        "role",
        "worked",
        "career",
    ]):
        source_hint = "experience"

    elif any(word in query_lower for word in [
        "education",
        "degree",
        "college",
        "university",
        "school",
        "study",
        "studied",
    ]):
        source_hint = "education"

    elif any(word in query_lower for word in [
        "skill",
        "skills",
        "technology",
        "technologies",
        "programming",
    ]):
        source_hint = "skills"

    elif any(word in query_lower for word in [
        "project",
        "projects",
        "built",
        "developed",
    ]):
        source_hint = "projects"

    elif any(word in query_lower for word in [
        "certificate",
        "certification",
        "certifications",
    ]):
        source_hint = "certificates"

    # --------------------------------
    # Projects
    # --------------------------------

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
                project_documents.append({
                    "text": document,
                    "source": source,
                })

        return project_documents[:k]

    # --------------------------------
    # Skills
    # --------------------------------

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
                skill_documents.append({
                    "text": document,
                    "source": source,
                })

        return skill_documents

    # --------------------------------
    # Semantic RAG retrieval
    # --------------------------------

    query_embedding = embed_texts(
        [query]
    )[0]

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