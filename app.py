import streamlit as st
import seagrass_cover
import testgrass

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

if st.sidebar.button("🌾 Testgrass", key="testgrass"):
    st.session_state.page = "testgrass"

# Affichage dynamique du contenu selon le bouton
if st.session_state.page == "seagrass":
    seagrass_cover.main()

elif st.session_state.page == "testgrass":
    testgrass.main()
