import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from rag_backend import get_ai_extraction_with_rag, parse_asmens_kodas

load_dotenv()

# --- MOCK LOGIN SYSTEM ---
if "current_user" not in st.session_state:
    st.session_state["current_user"] = "Dr. Jonas Gydytojas"

# --- SESSION STATE ---
if "field_data" not in st.session_state:
    st.session_state["field_data"] = {
        "vardas": "",
        "pavarde": "",
        "asm_kodas": "",
        "diag_kodas": "",
        "diag_pavadinimas": "",
        "diag_statusas": "+",
        "achi_kodas": "",
        "achi_pavadinimas": "",
        "pasitikejimo_lygis": 0,
        "paaiskinimas": "",
    }

st.set_page_config(
    page_title="NotaMeda | Digital F025/a-LK", page_icon="🏥", layout="wide"
)

st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    .stApp { max-width: 1200px; margin: 0 auto; }
    h1, h2, h3 { color: #1c3d5a; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; border-radius: 5px; height: 3em; font-weight: bold;}
    .section-header { margin-top: 2rem; margin-bottom: 1rem; color: #007bff; border-bottom: 2px solid #e9ecef; padding-bottom: 0.5rem;}
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #6c757d;
        text-align: center;
        padding: 10px 0;
        border-top: 1px solid #e9ecef;
        font-size: 0.9rem;
    }
    .footer a { color: #007bff; text-decoration: none; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

cols = st.columns([3, 1])
with cols[0]:
    st.title("🏥 NotaMeda")
    st.caption("Forma Nr. 025/a-LK | AI Apsilankymų Statistinė Kortelė")
with cols[1]:
    st.info(f"👤 Prisijungta: **{st.session_state['current_user']}**")

# --- AI EXTRACTION SECTION ---
with st.container():
    st.markdown(
        '<div class="section-header"><h4>✨ AI Automatinis Užpildymas</h4></div>',
        unsafe_allow_html=True,
    )

    col_text, col_settings = st.columns([3, 1])

    with col_settings:
        selected_model = "mistral/mistral-large-latest"
        st.success("RAG duomenų bazė pajungta ✔️")
        st.write(
            "Įklijuokite tekstą, ir AI automatiškai ištrauks duomenis bei įvertins savo patikimumą."
        )

    with col_text:
        doc_context = st.text_area(
            "Įklijuokite gydytojo pastabas arba paciento išrašą:",
            height=120,
            label_visibility="collapsed",
        )

        if st.button("🚀 Analizuoti ir užpildyti formą"):
            if doc_context:
                with st.spinner(f"AI analizuoja tekstą..."):
                    extracted = get_ai_extraction_with_rag(
                        doc_context, text_model=selected_model
                    )

                    for key in extracted:
                        if key in st.session_state["field_data"]:
                            st.session_state["field_data"][key] = extracted[key]

                    ak = st.session_state["field_data"].get("asm_kodas", "")
                    if ak:
                        b_date, gender = parse_asmens_kodas(ak)
                        if b_date:
                            st.session_state["field_data"]["gimimo_data"] = b_date
                        if gender:
                            st.session_state["field_data"]["lytis"] = gender

                    st.success(
                        "Forma sėkmingai užpildyta! Peržiūrėkite duomenis žemiau."
                    )
            else:
                st.warning("Pirma įveskite tekstą.")

# --- THE UNIFIED FORM ---
with st.form("pretty_medical_form"):
    st.markdown(
        '<div class="section-header"><h4>👤 Asmens Duomenys</h4></div>',
        unsafe_allow_html=True,
    )
    a1, a2, a3 = st.columns(3)
    with a1:
        st.text_input(
            "Vardas (10.0)", value=st.session_state["field_data"].get("vardas", "")
        )
        st.text_input(
            "Asmens kodas (7.0)",
            value=st.session_state["field_data"].get("asm_kodas", ""),
        )
    with a2:
        st.text_input(
            "Pavardė (11.0)", value=st.session_state["field_data"].get("pavarde", "")
        )
        st.date_input(
            "Gimimo data",
            value=st.session_state["field_data"].get("gimimo_data", None),
            format="YYYY-MM-DD",
        )
    with a3:
        gender_val = st.session_state["field_data"].get("lytis", "Vyras")
        st.radio(
            "Lytis",
            ["Vyras", "Moteris"],
            horizontal=True,
            index=0 if gender_val == "Vyras" else 1,
        )
        st.selectbox(
            "Draustumo tipas", ["Apdraustas PSD", "ES/EEE draudimas", "Nedraustas"]
        )

    st.markdown(
        '<div class="section-header"><h4>🩺 Klinikinė Informacija</h4></div>',
        unsafe_allow_html=True,
    )

    confidence = st.session_state["field_data"].get("pasitikejimo_lygis", 0)
    reasoning = st.session_state["field_data"].get("paaiskinimas", "")

    if confidence > 0:
        c1, c2 = st.columns([1, 3])
        with c1:
            if confidence >= 85:
                color = "green"
            elif confidence >= 60:
                color = "orange"
            else:
                color = "red"

            st.markdown(
                f"**AI Patikimumas:** <span style='color:{color}; font-size:1.2em; font-weight:bold;'>{confidence}%</span>",
                unsafe_allow_html=True,
            )
            st.progress(confidence / 100.0)
        with c2:
            st.info(f"**AI Analizė:** {reasoning}")
        st.write("")

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**Galutinė Diagnozė (TLK-10-AM)**")
        st.text_input(
            "Kodas (25.0)", value=st.session_state["field_data"].get("diag_kodas", "")
        )
        st.text_input(
            "Pavadinimas (26.0)",
            value=st.session_state["field_data"].get("diag_pavadinimas", ""),
        )

        status_val = st.session_state["field_data"].get("diag_statusas", "+")
        st.selectbox(
            "Statusas (27.0)",
            ["+", "-", "0"],
            index=["+", "-", "0"].index(status_val)
            if status_val in ["+", "-", "0"]
            else 0,
        )

    with m2:
        st.markdown("**Intervencija / Procedūra (ACHI)**")
        st.text_input(
            "Kodas (43.0)", value=st.session_state["field_data"].get("achi_kodas", "")
        )
        st.text_input(
            "Pavadinimas (44.0)",
            value=st.session_state["field_data"].get("achi_pavadinimas", ""),
        )

    st.markdown(
        '<div class="section-header"><h4>✅ Pateikimas</h4></div>',
        unsafe_allow_html=True,
    )
    f1, f2, f3 = st.columns(3)
    with f1:
        st.date_input("Apsilankymo data", format="YYYY-MM-DD")
    with f2:
        st.text_input(
            "Atsakingas Specialistas",
            value=st.session_state["current_user"],
            disabled=True,
        )
    with f3:
        st.text_input(
            "Pateikimo laikas",
            value=datetime.now().strftime("%Y-%m-%d %H:%M"),
            disabled=True,
        )

    st.markdown("---")
    submitted = st.form_submit_button("📁 Išsaugoti ir nusiųsti į sistemą")

if submitted:
    st.balloons()
    st.success("Formos duomenys sėkmingai išsaugoti DB.")

# --- FOOTER ---
st.markdown(
    """
    <div class="footer">
        NotaMeda © 2026 | Find us on <a href="https://github.com/masha170406/DeadlineDriven_VLK" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True,
)
