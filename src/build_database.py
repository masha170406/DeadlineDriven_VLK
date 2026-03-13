import pandas as pd
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import litellm
from dotenv import load_dotenv

load_dotenv()


class LiteLLMEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        response = litellm.embedding(model=self.model_name, input=input)
        return [data["embedding"] for data in response.data]


def build_vector_db():
    print("Building Enriched Medical Database...")

    agnostic_ef = LiteLLMEmbeddingFunction(model_name="mistral/mistral-embed")
    client = chromadb.PersistentClient(path="./vlk_chroma_db")

    # CRITICAL: We set the space to 'cosine' to get better discrimination
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

    def ingest_csv(csv_filename, collection):
        df = pd.read_csv(csv_filename)

        docs = []
        metadatas = []
        ids = []

        for _, row in df.iterrows():
            code = str(row["code"])
            title = str(row["description"])
            # We add a fallback if symptoms are missing
            symptoms = str(row.get("symptoms", ""))

            # Create the 'Super-Document' for high-precision search
            search_string = f"Kodas: {code}. Pavadinimas: {title}. Raktažodžiai ir požymiai: {symptoms}"

            docs.append(search_string)
            metadatas.append({"kodas": code, "pavadinimas": title})
            ids.append(code)

        collection.add(documents=docs, metadatas=metadatas, ids=ids)
        print(f"✅ Ingested {len(ids)} codes into {collection.name}")

    ingest_csv("data/top_50_tlk_10_am.csv", tlk_collection)
    ingest_csv("data/top_50_achi.csv", achi_collection)


if __name__ == "__main__":
    build_vector_db()
