from pathlib import Path
import os
import threading

os.environ["ANONYMIZED_TELEMETRY"] = "False"

from app.core.config import settings

ROOT = Path(__file__).resolve().parents[2]

client = None
embedding_model = None
collection = None

_init_lock = threading.Lock()

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_collection():
    global client, embedding_model, collection

    if collection is not None:
        return collection

    with _init_lock:
        if collection is not None:
            return collection

        print("RAG: starting Chroma initialization", flush=True)

        import chromadb
        from fastembed import TextEmbedding

        print("RAG: creating Chroma client", flush=True)

        client = chromadb.PersistentClient(
            path=str(ROOT / settings.chroma_dir)
        )

        print("RAG: Chroma client ready", flush=True)

        print("RAG: loading FastEmbed MiniLM", flush=True)

        embedding_model = TextEmbedding(
            model_name=MODEL_NAME
        )

        print("RAG: embedding model ready", flush=True)

        collection = client.get_or_create_collection(
            name="portfolio_knowledge"
        )

        print("RAG: collection ready", flush=True)

    return collection


def embed_texts(texts: list[str]):
    get_collection()

    embeddings = embedding_model.embed(texts)

    return [embedding.tolist() for embedding in embeddings]


def chunk_text(text: str, size: int = 700, overlap: int = 100):
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


def index_documents(documents: list[dict]):
    collection = get_collection()

    ids = []
    texts = []
    metadatas = []

    for document in documents:
        chunks = chunk_text(document["text"])

        for index, chunk in enumerate(chunks):
            ids.append(f"{document['id']}-{index}")
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


def retrieve(query: str, k: int = 5):
    collection = get_collection()

    query_lower = query.lower()
    source_hint = None

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

    if source_hint == "projects":
        all_data = collection.get(
            include=["documents", "metadatas"]
        )

        project_documents = []

        for document, metadata in zip(
            all_data.get("documents", []),
            all_data.get("metadatas", []),
        ):
            source = (metadata or {}).get("source", "")

            if source.startswith("project:"):
                project_documents.append({
                    "text": document,
                    "source": source,
                })

        return project_documents[:k]

    if source_hint == "skills":
        all_data = collection.get(
            include=["documents", "metadatas"]
        )

        skill_documents = []

        for document, metadata in zip(
            all_data.get("documents", []),
            all_data.get("metadatas", []),
        ):
            source = (metadata or {}).get("source", "")

            if source == "skills":
                skill_documents.append({
                    "text": document,
                    "source": source,
                })

        return skill_documents

    query_embedding = embed_texts([query])[0]

    if source_hint:
        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where={"source": source_hint},
        )
    else:
        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    return [
        {
            "text": document,
            "source": (metadata or {}).get(
                "source",
                "portfolio"
            ),
        }
        for document, metadata in zip(
            documents,
            metadatas,
        )
    ]