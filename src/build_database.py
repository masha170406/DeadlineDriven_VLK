import pandas as pd
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import litellm
import os
from dotenv import load_dotenv

load_dotenv()


class LiteLLMEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        response = litellm.embedding(model=self.model_name, input=input)
        return [data["embedding"] for data in response.data]


def build_vector_db():
    # Use an absolute path or a path relative to the app root to avoid confusion in Docker
    db_path = os.path.join(os.getcwd(), "vlk_chroma_db")
    print(f"Checking database at: {db_path}")

    agnostic_ef = LiteLLMEmbeddingFunction(model_name="mistral/mistral-embed")
    client = chromadb.PersistentClient(path=db_path)

    tlk_collection = client.get_or_create_collection(
        name="tlk_10_diagnoses",
        embedding_function=agnostic_ef,
        metadata={"hnsw:space": "cosine"},
    )

    achi_collection = client.get_or_create_collection(
        name="achi_interventions",
        embedding_function=agnostic_ef,
        metadata={"hnsw:space": "cosine"},
    )

    def ingest_csv(csv_path, collection):
        # IDEMPOTENCY CHECK: If collection has data, skip ingestion
        if collection.count() > 0:
            print(
                f"⚠️ Collection '{collection.name}' already contains {collection.count()} items. Skipping."
            )
            return

        if not os.path.exists(csv_path):
            print(f"❌ File not found: {csv_path}")
            return

        print(f"📥 Ingesting {csv_path}...")
        df = pd.read_csv(csv_path)
        docs, metadatas, ids = [], [], []

        for _, row in df.iterrows():
            code = str(row["code"])
            title = str(row["description"])
            symptoms = str(row.get("symptoms", ""))
            search_string = (
                f"Kodas: {code}. Pavadinimas: {title}. Raktažodžiai: {symptoms}"
            )

            docs.append(search_string)
            metadatas.append({"kodas": code, "pavadinimas": title})
            ids.append(code)

        collection.add(documents=docs, metadatas=metadatas, ids=ids)
        print(f"✅ Successfully ingested {len(ids)} items.")

    # Paths adjusted for the src/ structure
    ingest_csv("data/top_50_tlk_10_am.csv", tlk_collection)
    ingest_csv("data/top_50_achi.csv", achi_collection)


if __name__ == "__main__":
    build_vector_db()
