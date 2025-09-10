import streamlit as st
import seagrass_cover
import seagrass_cover_zones
import dugong_grazing
import drone_mapping

st.set_page_config(page_title="Green Guardian", page_icon="🌱", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = "seagrass"

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Seagrass Cover", "Zones & Richness", "Dugong Grazing", "Drone Mapping"],
    index=["Seagrass Cover", "Zones & Richness", "Dugong Grazing", "Drone Mapping"].index(
        st.session_state.get("page_title", "Seagrass Cover")
    )
)

if page == "Seagrass Cover":
    st.session_state.page_title = "Seagrass Cover"
    seagrass_cover.main()
elif page == "Zones & Richness":
    st.session_state.page_title = "Zones & Richness"
    seagrass_cover_zones.main()
elif page == "Dugong Grazing":
    st.session_state.page_title = "Dugong Grazing"
    dugong_grazing.main()
else:
    st.session_state.page_title = "Drone Mapping"
    drone_mapping.main()
