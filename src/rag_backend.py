import json
from datetime import datetime
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import litellm
from dotenv import load_dotenv
from prompts import VLK_SYSTEM_PROMPT

load_dotenv()


# --- 1. LLM-AGNOSTIC EMBEDDING FUNCTION ---
class LiteLLMEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        response = litellm.embedding(model=self.model_name, input=input)
        return [data["embedding"] for data in response.data]


def get_chroma_collections():
    client = chromadb.PersistentClient(path="./vlk_chroma_db")

    # Privalome naudoti tą patį modelį, kuriuo kūrėme duomenų bazę
    agnostic_ef = LiteLLMEmbeddingFunction(model_name="mistral/mistral-embed")

    tlk_collection = client.get_collection(
        name="tlk_10_diagnoses", embedding_function=agnostic_ef
    )
    achi_collection = client.get_collection(
        name="achi_interventions", embedding_function=agnostic_ef
    )

    return tlk_collection, achi_collection


def retrieve_relevant_codes(doctor_note, collection, n_results=3):
    try:
        results = collection.query(query_texts=[doctor_note], n_results=n_results)
        formatted_context = ""
        for i in range(len(results["ids"][0])):
            code = results["ids"][0][i]
            description = results["documents"][0][i]
            formatted_context += f"- Kodas: {code} | Pavadinimas: {description}\n"
        return formatted_context
    except Exception as e:
        print(f"ChromaDB klaida: {e}")
        return "Nerasta atitikmenų."


def get_ai_extraction_with_rag(doctor_note, text_model="mistral/mistral-large-latest"):
    """
    Agnostic RAG function. Accepts any model from the Streamlit UI.
    """
    tlk_coll, achi_coll = get_chroma_collections()

    # 1. RETRIEVE
    tlk_context = retrieve_relevant_codes(doctor_note, tlk_coll, n_results=3)
    achi_context = retrieve_relevant_codes(doctor_note, achi_coll, n_results=3)

    # 2. AUGMENT (Format the imported prompt)
    prompt = VLK_SYSTEM_PROMPT.format(
        doctor_note=doctor_note, tlk_context=tlk_context, achi_context=achi_context
    )

    # 3. GENERATE
    try:
        response = litellm.completion(
            model=text_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw_content = response.choices[0].message.content.strip()
        return json.loads(raw_content)
    except Exception as e:
        print(f"LiteLLM Error: {e}")
        return {}


def parse_asmens_kodas(ak: str):
    """Extracts birthdate and gender from a valid Lithuanian Personal ID."""
    if not ak or len(ak) != 11 or not ak.isdigit():
        return None, None

    g_char = int(ak[0])
    yy, mm, dd = int(ak[1:3]), int(ak[3:5]), int(ak[5:7])

    gender = "Vyras" if g_char % 2 != 0 else "Moteris"

    if g_char in (1, 2):
        year = 1800 + yy
    elif g_char in (3, 4):
        year = 1900 + yy
    elif g_char in (5, 6):
        year = 2000 + yy
    else:
        return None, None

    try:
        return datetime(year, mm, dd).date(), gender
    except ValueError:
        return None, None
