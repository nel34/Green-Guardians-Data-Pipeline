import streamlit as st

TRANSLATIONS = {
    "en": {
        # Navigation
        "nav_seagrass": "🌿 Seagrass Cover",
        "nav_seagrass_zones": "🌱 Seagrass Cover Zones",
        "nav_dugong": "🦭 Dugong – Grazing",
        "nav_drone": "🚁 Drone – Mapping",
        "nav_cyano": "🦠 Cyanobacteria Evidence",
        "select_language": "Select language",
        # Seagrass cover page
        "title_seagrass": "🌿 Average Seagrass Cover",
        "select_years": "Select years of interest:",
        "no_year_selected": "No year selected. Please select at least one year to display the data.",
        "avg_by_month_header": "Average Seagrass Cover by Month",
        "select_months": "Select months:",
        "no_month_data": "No data for the selected months.",
        "chart_avg_cover": "Average Seagrass Cover (%)",
        "chart_avg_cover_by_month": "Average % Seagrass Cover by Month",
        # Drone mapping
        "title_drone": "🚁 Drone Mapping",
        "no_drone_data": "No seagrass mapping data available for the current selection.",
        "seagrass_mapped_surface": "Seagrass mapped surface",
        # Cyanobacteria
        "title_cyano": "🦠 Cyanobacteria Evidence",
        "no_cyano_column": "No cyanobacteria column in dataset.",
        "no_cyano_data": "No cyanobacteria evidence data for the selected filters.",
        # Dugong
        "title_dugong": "🦭 Dugong – Grazing Traces and Seagrass Condition",
        "no_grazing_data": "No grazing data for this selection.",
        "grazing_tab1": "Grazing frequency by zone/year",
        "grazing_tab2": "Impact on seagrass",
        # Zones page
        "title_zones": "🌱 Seagrass Meadows Exploration (Species Richness & Cover)",
        "data_selection": "Data Selection",
        "no_species_data": "No species richness data for this selection.",
        "no_cover_data": "No cover data for this selection.",
    },
    "th": {
        # Navigation (Thai approximative translations)
        "nav_seagrass": "🌿 ครอบคลุมหญ้าทะเล",
        "nav_seagrass_zones": "🌱 โซนหญ้าทะเล",
        "nav_dugong": "🦭 ยีราฟ Dugong – ร่องรอยการกิน",
        "nav_drone": "🚁 การทำแผนที่ด้วยโดรน",
        "nav_cyano": "🦠 หลักฐานไซยาโนแบคทีเรีย",
        "select_language": "เลือกภาษา",
        # Seagrass cover page
        "title_seagrass": "🌿 ค่าเฉลี่ยการคลุมหญ้าทะเล",
        "select_years": "เลือกปีที่สนใจ:",
        "no_year_selected": "ยังไม่ได้เลือกปี โปรดเลือกอย่างน้อยหนึ่งปีเพื่อแสดงข้อมูล",
        "avg_by_month_header": "ค่าเฉลี่ยการคลุมหญ้าทะเลตามเดือน",
        "select_months": "เลือกเดือน:",
        "no_month_data": "ไม่มีข้อมูลสำหรับเดือนที่เลือก",
        "chart_avg_cover": "ค่าเฉลี่ยการคลุมหญ้าทะเล (%)",
        "chart_avg_cover_by_month": "ค่าเฉลี่ย % การคลุมหญ้าทะเลตามเดือน",
        # Drone mapping
        "title_drone": "🚁 การทำแผนที่ด้วยโดรน",
        "no_drone_data": "ไม่มีข้อมูลการทำแผนที่หญ้าทะเลสำหรับการเลือกปัจจุบัน",
        "seagrass_mapped_surface": "พื้นที่หญ้าทะเลที่ถูกทำแผนที่",
        # Cyanobacteria
        "title_cyano": "🦠 หลักฐานไซยาโนแบคทีเรีย",
        "no_cyano_column": "ไม่มีคอลัมน์ไซยาโนแบคทีเรียในชุดข้อมูล",
        "no_cyano_data": "ไม่มีข้อมูลหลักฐานไซยาโนแบคทีเรียสำหรับตัวกรองที่เลือก",
        # Dugong
        "title_dugong": "🦭 Dugong – ร่องรอยการกินและสภาพหญ้าทะเล",
        "no_grazing_data": "ไม่มีข้อมูลการกัดหญ้าสำหรับการเลือกนี้",
        "grazing_tab1": "ความถี่การกินตามโซน/ปี",
        "grazing_tab2": "ผลกระทบต่อหญ้าทะเล",
        # Zones page
        "title_zones": "🌱 สำรวจทุ่งหญ้าทะเล (ความหลากหลายชนิด & การคลุม)",
        "data_selection": "การเลือกข้อมูล",
        "no_species_data": "ไม่มีข้อมูลความหลากหลายชนิดสำหรับการเลือกนี้",
        "no_cover_data": "ไม่มีข้อมูลการคลุมสำหรับการเลือกนี้",
    }
}

def t(key: str, **kwargs) -> str:
    """Return translated string for current language stored in st.session_state.lang."""
    lang = st.session_state.get("lang", "en")
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text