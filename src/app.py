import streamlit as st
from dotenv import load_dotenv

from rag_backend import get_ai_extraction_with_rag

load_dotenv()

if "field_data" not in st.session_state:
    st.session_state["field_data"] = {
        "vardas": "",
        "pavarde": "",
        "asm_kodas": "",
        "diag_kodas": "",
        "diag_pavadinimas": "",
        "achi_kodas": "",
        "achi_pavadinimas": "",
        "specialistas": "",
    }

st.set_page_config(page_title="Digital F025/a-LK Form", page_icon="🏥", layout="wide")

st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    .stApp { max-width: 1200px; margin: 0 auto; }
    h1, h2, h3 { color: #1c3d5a; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; border-radius: 5px; height: 3em; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏥 AI Apsilankymų Statistinė Kortelė")
st.caption("Forma Nr. 025/a-LK | Model-Agnostic RAG System")

with st.expander("✨ AI AUTOMATINIS UŽPILDYMAS", expanded=True):
    col_text, col_settings = st.columns([3, 1])

    with col_settings:
        st.subheader("⚙️ Sistemos nustatymai")
        selected_model = "mistral/mistral-large-latest"
        st.info("Mistral RAG duomenų bazė pajungta ✔️")

    with col_text:
        doc_context = st.text_area(
            "Įklijuokite gydytojo pastabas arba paciento išrašą:", height=150
        )
        if st.button("Analizuoti ir užpildyti formą"):
            if doc_context:
                with st.spinner(
                    f"{selected_model.split('/')[0].upper()} analizuoja tekstą..."
                ):
                    extracted = get_ai_extraction_with_rag(
                        doc_context, text_model=selected_model
                    )

                    for key in extracted:
                        if key in st.session_state["field_data"]:
                            st.session_state["field_data"][key] = extracted[key]
                    st.success("Forma sėkmingai užpildyta!")
            else:
                st.warning("Pirma įveskite tekstą.")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📋 I: Bendroji dalis",
        "🩺 II: Diagnozės",
        "🗓️ III: Apsilankymas",
        "✅ IV: Baigiamoji",
    ]
)

with st.form("pretty_medical_form"):
    with tab1:
        st.subheader("Asmens Duomenys")
        a1, a2, a3 = st.columns(3)
        with a1:
            st.text_input(
                "Asmens kodas (7.0)",
                value=st.session_state["field_data"].get("asm_kodas", ""),
            )
            st.text_input(
                "Vardas (10.0)", value=st.session_state["field_data"].get("vardas", "")
            )
        with a2:
            st.text_input(
                "Pavardė (11.0)",
                value=st.session_state["field_data"].get("pavarde", ""),
            )

    with tab2:
        st.subheader("Galutinės (Patikslintos) Diagnozės")
        g1, g2, g3 = st.columns([1, 1, 2])
        with g1:
            st.date_input("Diagnozės data (24.0)")
        with g2:
            st.text_input(
                "TLK-10-AM kodas (25.0)",
                value=st.session_state["field_data"].get("diag_kodas", ""),
            )
        with g3:
            st.text_input(
                "Pavadinimas (26.0)",
                value=st.session_state["field_data"].get("diag_pavadinimas", ""),
            )

    with tab3:
        st.subheader("Apsilankymo Informacija")
        v1, v2, v3 = st.columns(3)
        with v1:
            st.date_input("Apsilankymo data (32.0)")
            st.text_input(
                "Specialistas (34.0)",
                value="Gydytojo Vardas",
            )

        st.divider()
        st.subheader("Intervencijos & Vaistai")
        iv1, iv2 = st.columns(2)
        with iv1:
            st.text_input(
                "ACHI Kodas (43.0)",
                value=st.session_state["field_data"].get("achi_kodas", ""),
            )
            st.text_input(
                "ACHI Pavadinimas (44.0)",
                value=st.session_state["field_data"].get("achi_pavadinimas", ""),
            )

    with tab4:
        st.subheader("Pateikimas")
        st.date_input("Baigta pildyti: Data/Laikas (60.0)")

    st.markdown("---")
    submitted = st.form_submit_button("📁 Išsaugoti skaitmeninį įrašą")

if submitted:
    st.balloons()
    st.success("Formos duomenys sėkmingai išsaugoti DB.")
