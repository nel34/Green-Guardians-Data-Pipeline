import streamlit as st

import seagrass_cover
import seagrass_cover_zones
import dugong_grazing  
import drone_mapping
import cyanobacteria_evidence

st.set_page_config(page_title="Green Guardian", page_icon="🌱", layout="wide")



# ensure translation helper
import translations
t = translations.t



# small spacer between selector and menu header
st.sidebar.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# Menu header
st.sidebar.markdown(f'<p style="font-size:35px; font-weight:bold;">📌 {t("menu_title")}</p>', unsafe_allow_html=True)
st.sidebar.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)


# Sidebar navigation with small vertical spacing between buttons
if 'page' not in st.session_state:
    st.session_state.page = "seagrass"

if st.sidebar.button(t("nav_seagrass"), key="seagrass"):
    st.session_state.page = "seagrass"

if st.sidebar.button(t("nav_seagrass_zones"), key="seagrass_cover_zones"):
    st.session_state.page = "seagrass_cover_zones"

if st.sidebar.button(t("nav_dugong"), key="dugong_grazing"):
    st.session_state.page = "dugong_grazing"

if st.sidebar.button(t("nav_drone"), key="drone_mapping"):
    st.session_state.page = "drone_mapping"

if st.sidebar.button(t("nav_cyano"), key="cyanobacteria_evidence"):
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
    
st.sidebar.markdown('<div style="height:300px;"></div>', unsafe_allow_html=True)
    
# ensure session_state.lang exists
if "lang" not in st.session_state:
    st.session_state.lang = "en"

def _on_lang_change():
    # met à jour la langue active ; pas d'appel à experimental_rerun ici
    st.session_state.lang = st.session_state.lang_select

# compact selector (langue stockée dans st.session_state.lang_select)
col_left, col_right = st.sidebar.columns([2,1])
with col_left:
    st.selectbox(
        "",
        options=["en", "th"],
        format_func=lambda v: {"en": "English", "th": "ไทย"}[v],
        index=0 if st.session_state.lang == "en" else 1,
        key="lang_select",
        on_change=_on_lang_change
    )
