import streamlit as st
import seagrass_cover
import seagrass_cover_zones
import dugong_grazing  
import drone_mapping
import cyanobacteria_evidence

st.set_page_config(page_title="Green Guardian", page_icon="🌱", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = "seagrass"

# Sidebar stylisée
st.sidebar.markdown("""
<style>
button.sidebar-button {
    background-color: transparent;
    border: none;
    color: white;
    font-size: 18px;
    text-align: left;
    padding: 10px 5px;
    width: 100%;
    cursor: pointer;
}

button.sidebar-button:hover {
    background-color: #444;
    font-weight: bold;
}
</style>

<h1 style="margin-bottom: 20px; font-size: 28px;">📌 Navigation</h1>
""", unsafe_allow_html=True)

# Boutons de navigation
if st.sidebar.button("🌿 Seagrass Cover", key="seagrass"):
    st.session_state.page = "seagrass"
if st.sidebar.button("🌱 Seagrass Cover Zones", key="seagrass_cover_zones"):
    st.session_state.page = "seagrass_cover_zones"
if st.sidebar.button("🐾 Dugong – Pâturage", key="dugong_grazing"):
    st.session_state.page = "dugong_grazing"
if st.sidebar.button("🛩️ Drone – Mapping", key="drone_mapping"):
    st.session_state.page = "drone_mapping"
if st.sidebar.button("🔵 Cyanobacteria Evidence", key="cyanobacteria_evidence"):
    st.session_state.page = "cyanobacteria_evidence"

# Affichage dynamique du contenu selon le bouton
if st.session_state.page == "seagrass":
    seagrass_cover.main()
elif st.session_state.page == "seagrass_cover_zones":
    seagrass_cover_zones.main()
elif st.session_state.page == "dugong_grazing":
    dugong_grazing.main()
elif st.session_state.page == "drone_mapping":
    drone_mapping.main()
elif st.session_state.page == "cyanobacteria_evidence":
    cyanobacteria_evidence.main()
