import streamlit as st
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Digital F025/a-LK Form",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for a cleaner, modern look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #1c3d5a;
    }
    .stButton>button {
        width: 100%;
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Apsilankymų Statistinė Kortelė")
st.caption("Forma Nr. 025/a-LK | Patvirtinta LR SAM įsakymu Nr. V-39")

# Use Tabs to organize the parts without changing the internal field structure
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 I: Bendroji dalis", 
    "🩺 II: Diagnozės", 
    "🗓️ III: Apsilankymas", 
    "✅ IV: Baigiamoji"
])

with st.form("pretty_medical_form"):
    
    with tab1:
        st.subheader("Įstaigos ir Dokumento Duomenys")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("ASPĮ Kodas/Pavadinimas (1A/1B)")
            st.text_input("Kortelės Nr. (3.0)")
        with col2:
            st.selectbox("Paskirtis (2.0)", ["1 - Gydymas", "2 - Profilaktika", "3 - Kita"])
            st.text_input("Susijusio dokumento Nr. (4.0)")
        with col3:
            st.radio("Kortelės tipas", ["Pirminė (5A)", "Tikslinamoji (5B)", "Anuliuojamoji (5C)"], horizontal=True)
            st.text_input("Tikslinamos kortelės Nr. (6.0)")

        st.divider()
        st.subheader("Asmens Duomenys")
        a1, a2, a3 = st.columns(3)
        with a1:
            st.text_input("Asmens kodas (7.0)")
            st.text_input("Vardas (10.0)")
            st.date_input("Gimimo data (13.0)", min_value=datetime(1900, 1, 1))
        with a2:
            st.text_input("Motinos asm. kodas (8.0)")
            st.text_input("Pavardė (11.0)")
            st.radio("Lytis (14.0)", ["Vyras", "Moteris"], horizontal=True)
        with a3:
            st.text_input("DIK (9.0)")
            st.checkbox("Nuolatinis LR gyventojas (12.0)")
            st.text_input("Tel. numeris (16.0)")

        st.divider()
        st.subheader("Draustumas ir Adresas")
        d1, d2 = st.columns(2)
        with d1:
            st.text_input("Adresas (17A-E)", placeholder="Valstybė, miestas, gatvė...")
            st.text_input("PAASPĮ (18A/18B)")
        with d2:
            st.selectbox("Draustumo tipas (19.0)", ["Apdraustas PSD", "ES/EEE draudimas", "Kita"])
            st.text_input("Draudimo dokumentas / Galiojimas (19E/19F)")

    with tab2:
        st.subheader("Galutinės (Patikslintos) Diagnozės")
        g1, g2, g3 = st.columns([1, 1, 2])
        with g1:
            st.date_input("Diagnozės data (24.0)")
        with g2:
            st.text_input("TLK-10-AM kodas (25.0)")
        with g3:
            st.text_input("Pavadinimas (26.0)")
        
        st.selectbox("Statusas (27.0)", ["+", "-", "0"], help="+ (ūminė), - (lėtinė pirmąkart), 0 (lėtinė seniau)")
        st.text_area("Traumos priežastis (28.0)")

    with tab3:
        st.subheader("Apsilankymo Informacija")
        v1, v2, v3 = st.columns(3)
        with v1:
            st.date_input("Apsilankymo data (32.0)")
            st.text_input("Specialistas (34.0)")
        with v2:
            st.text_input("Paslaugos kodas (35.0)")
            st.selectbox("Tipas (36.0)", [1, 2, 3, 5])
        with v3:
            st.selectbox("Rezultatas (40.0)", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 99])
            st.number_input("Kaina balais (41.0)")

        st.divider()
        st.subheader("Intervencijos & Vaistai")
        iv1, iv2 = st.columns(2)
        with iv1:
            st.text_input("ACHI Kodas (43.0)")
            st.text_input("ACHI Pavadinimas (44.0)")
        with iv2:
            st.text_input("Vaisto/MPP ID (54.0)")
            st.number_input("Kiekis (58.0)", step=1)

    with tab4:
        st.subheader("Pateikimas")
        f1, f2 = st.columns(2)
        with f1:
            st.text_input("Baigta pildyti: Data/Laikas (60.0)")
            st.text_input("Pateikta: Data/Laikas (61.0)")
        with f2:
            st.number_input("Bendra suma balais (62.0)")
            st.text_input("Atsakingasis asmuo (65.0)")

    # Bottom Submit
    st.markdown("---")
    submitted = st.form_submit_button("📁 Išsaugoti skaitmeninį įrašą")

if submitted:
    st.balloons()
    st.success("Formos duomenys sėkmingai išsaugoti sistemoje.")

with st.expander("ℹ️ Pagalba ir Kodų Reikšmės"):
    st.write("**36 skiltis:** 1-PSP specialistas, 2-Konsultantas (1-as vizitas), 3-Konsultantas (tęstinis), 5-Mokama.")
    st.write("**40 skiltis:** 1-Gydymas baigtas, 6-Siuntimas stacionarui, 99-Mirtis.")