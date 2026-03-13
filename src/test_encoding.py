import streamlit as st
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import litellm
from dotenv import load_dotenv

load_dotenv()

# --- 1. CONFIGURATION ---
# Ensure this matches your build_database.py exactly!
EMBEDDING_MODEL = "mistral/mistral-embed"
DB_PATH = "./vlk_chroma_db"


class LiteLLMEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        response = litellm.embedding(model=self.model_name, input=input)
        return [data["embedding"] for data in response.data]


# --- 2. DB CONNECTION ---
@st.cache_resource
def get_collections():
    client = chromadb.PersistentClient(path=DB_PATH)
    agnostic_ef = LiteLLMEmbeddingFunction(model_name=EMBEDDING_MODEL)

    tlk = client.get_collection(name="tlk_10_diagnoses", embedding_function=agnostic_ef)
    achi = client.get_collection(
        name="achi_interventions", embedding_function=agnostic_ef
    )
    return tlk, achi


# --- 3. UI LAYOUT ---
st.set_page_config(page_title="RAG Debugger", layout="wide")
st.title("🔍 RAG Semantic Search Debugger")
st.write("Test how well the Vector Database understands your medical notes.")

tlk_coll, achi_coll = get_collections()

query = st.text_input(
    "Enter a medical note or symptom (Lithuanian):",
    placeholder="e.g., prastai matau į tolį",
)

col1, col2 = st.columns(2)

if query:
    # --- 4. SEMANTIC SEARCH ---
    with st.spinner("Searching vectors..."):
        # Search Diagnosis
        tlk_res = tlk_coll.query(query_texts=[query], n_results=5)
        # Search Interventions
        achi_res = achi_coll.query(query_texts=[query], n_results=5)

    with col1:
        st.subheader("🩺 Top Diagnosis Matches (TLK-10)")
        for i in range(len(tlk_res["ids"][0])):
            score = tlk_res["distances"][0][i]
            # Lower distance means it's mathematically "closer" in meaning
            st.metric(label=f"{tlk_res['ids'][0][i]}", value=f"Score: {score:.4f}")
            st.write(f"**Description:** {tlk_res['documents'][0][i]}")
            st.divider()

    with col2:
        st.subheader("🛠️ Top Intervention Matches (ACHI)")
        for i in range(len(achi_res["ids"][0])):
            score = achi_res["distances"][0][i]
            st.metric(label=f"{achi_res['ids'][0][i]}", value=f"Score: {score:.4f}")
            st.write(f"**Description:** {achi_res['documents'][0][i]}")
            st.divider()

    # --- 5. TECHNICAL INFO ---
    with st.expander("Technical: View Raw Vector Search Metadata"):
        st.json(tlk_res)
else:
    st.info("Type something above to see the vector database in action.")
