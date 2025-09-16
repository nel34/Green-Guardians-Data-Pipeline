import streamlit as st
import translations

import seagrass_cover
import seagrass_cover_zones
import dugong_grazing  
import drone_mapping
import cyanobacteria_evidence

st.set_page_config(page_title="Green Guardian", page_icon="🌱", layout="wide")

# initialize language
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Sidebar language selector
lang = st.sidebar.selectbox(
    translations.t("select_language"),
    options=[("English", "en"), ("ไทย", "th")],
    format_func=lambda v: v[0],
    index=0 if st.session_state.lang == "en" else 1,
)
# store code in session_state
st.session_state.lang = lang[1]

# Sidebar navigation (use translations)
if 'page' not in st.session_state:
    st.session_state.page = "seagrass"

if st.sidebar.button(translations.t("nav_seagrass"), key="seagrass"):
    st.session_state.page = "seagrass"
if st.sidebar.button(translations.t("nav_seagrass_zones"), key="seagrass_cover_zones"):
    st.session_state.page = "seagrass_cover_zones"
if st.sidebar.button(translations.t("nav_dugong"), key="dugong_grazing"):
    st.session_state.page = "dugong_grazing"
if st.sidebar.button(translations.t("nav_drone"), key="drone_mapping"):
    st.session_state.page = "drone_mapping"
if st.sidebar.button(translations.t("nav_cyano"), key="cyanobacteria_evidence"):
    st.session_state.page = "cyanobacteria_evidence"

# Display selected page
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
