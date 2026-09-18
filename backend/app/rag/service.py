from pathlib import Path
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from app.core.config import settings

ROOT = Path(__file__).resolve().parents[2]
client = None
embedder = None
collection = None

def get_collection():
    global client, embedder, collection

    if collection is None:
        print("RAG: starting Chroma initialization", flush=True)

        client = chromadb.PersistentClient(
            path=str(ROOT / settings.chroma_dir)
        )

        print("RAG: Chroma client ready", flush=True)

        embedder = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        print("RAG: embedding model ready", flush=True)

        collection = client.get_or_create_collection(
            name="portfolio_knowledge",
            embedding_function=embedder
        )

        print("RAG: collection ready", flush=True)

    return collection

def chunk_text(text: str, size: int = 700, overlap: int = 100):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start:start+size]))
        start += max(1, size-overlap)
    return [c for c in chunks if c.strip()]

def index_documents(documents: list[dict]):
    collection = get_collection()
    ids, texts, metas = [], [], []
    for doc in documents:
        for i, chunk in enumerate(chunk_text(doc["text"])):
            ids.append(f"{doc['id']}-{i}"); texts.append(chunk); metas.append({"source": doc["source"]})
    if ids:
        collection.upsert(ids=ids, documents=texts, metadatas=metas)
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
        "career"
    ]):
        source_hint = "experience"

    elif any(word in query_lower for word in [
        "education",
        "degree",
        "college",
        "university",
        "school",
        "study",
        "studied"
    ]):
        source_hint = "education"

    elif any(word in query_lower for word in [
        "skill",
        "skills",
        "technology",
        "technologies",
        "programming"
    ]):
        source_hint = "skills"

    elif any(word in query_lower for word in [
        "project",
        "projects",
        "built",
        "developed"
    ]):
        source_hint = "projects"

    elif any(word in query_lower for word in [
        "certificate",
        "certification",
        "certifications"
    ]):
        source_hint = "certificates"

    # Projects use source values like:
    # project:FraudShield AI
    # project:MultiGenAI...
    if source_hint == "projects":
        all_data = collection.get(
            include=["documents", "metadatas"]
        )

        project_docs = []

        for doc, meta in zip(
            all_data.get("documents", []),
            all_data.get("metadatas", [])
        ):
            source = (meta or {}).get("source", "")

            if source.startswith("project:"):
                project_docs.append({
                    "text": doc,
                    "source": source
                })

        return project_docs[:k]

    if source_hint == "skills":
           all_data = collection.get(
             include=["documents", "metadatas"]
            )

           skill_docs = []

           for doc, meta in zip(
              all_data.get("documents", []),
              all_data.get("metadatas", [])
           ):
             source = (meta or {}).get("source", "")

             if source == "skills":
                skill_docs.append({
                    "text": doc,
                    "source": source
                })

           return skill_docs

    # Other categories use exact metadata values
    if source_hint:
        result = collection.query(
            query_texts=[query],
            n_results=k,
            where={"source": source_hint}
        )
    else:
        result = collection.query(
            query_texts=[query],
            n_results=k
        )

    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]

    return [
        {
            "text": d,
            "source": (m or {}).get("source", "portfolio")
        }
        for d, m in zip(docs, metas)
    ]