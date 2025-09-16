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
        # Tabs / page fragments
        "tab_species_zone": "Species Richness by Zone",
        "tab_species_month": "Species Richness by Month",
        "tab_seagrass_cover": "Seagrass Cover",
        # Species richness (zones)
        "avg_species_by_zone_title": "Average Species Richness by Zone",
        "species_by_zone_chart_title": "Species Richness by Zone",
        "avg_species_y_label": "Average Species Richness",
        "zone_x_label": "Zone",
        "month_x_label": "Month",
        "global_species_richness": "Global average species richness:",
        "download_filtered_data": "Download filtered data (CSV)",
        # Species by month / small bar chart
        "avg_species_by_month_title": "Average Species Richness by Month",
        # Seagrass cover by zone
        "seagrass_cover_comparison_title": "Seagrass Cover Comparison by Zone ({months} - {years})",
        "percent_cover_y_label": "% Cover",
        # Drone mapping
        "mapped_surface_title": "Mapped Seagrass Surface by Month and Year",
        "mapped_surface_y_label": "Mapped surface (m²)",
        # Cyanobacteria
        "cyano_chart_title": "Cyanobacteria Evidence by Month and Year",
        "cyano_y_label": "Cyanobacteria evidence (units)",
        # Dugong
        "grazing_frequency_title": "Grazing frequency by zone and year",
        "grazing_impact_title": "Relationship between grazing and seagrass cover",
        "grazing_zone_label": "Zone",
        "grazing_y_label": "Frequency / Count",
        # Generic axis labels
        "x_year": "Year",
        "y_percent_cover": "% Cover",
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
        # Tabs / page fragments
        "tab_species_zone": "ความหลากหลายชนิดตามโซน",
        "tab_species_month": "ความหลากหลายชนิดตามเดือน",
        "tab_seagrass_cover": "การคลุมหญ้าทะเล",
        "avg_species_by_zone_title": "ค่าเฉลี่ยความหลากหลายชนิดตามโซน",
        "species_by_zone_chart_title": "ความหลากหลายชนิดตามโซน",
        "avg_species_y_label": "ความหลากหลายชนิดเฉลี่ย",
        "zone_x_label": "โซน",
        "month_x_label": "เดือน",
        "global_species_richness": "ค่าเฉลี่ยความหลากหลายชนิด (ทั่ว):",
        "download_filtered_data": "ดาวน์โหลดข้อมูลกรอง (CSV)",
        "avg_species_by_month_title": "ค่าเฉลี่ยความหลากหลายชนิดตามเดือน",
        "seagrass_cover_comparison_title": "การเปรียบเทียบการคลุมหญ้าทะเลตามโซน ({months} - {years})",
        "percent_cover_y_label": "% การคลุม",
        "mapped_surface_title": "พื้นที่หญ้าทะเลที่ถูกทำแผนที่ตามเดือนและปี",
        "mapped_surface_y_label": "พื้นที่ที่ทำแผนที่ (m²)",
        "cyano_chart_title": "หลักฐานไซยาโนแบคทีเรียตามเดือนและปี",
        "cyano_y_label": "หลักฐานไซยาโนแบคทีเรีย (หน่วย)",
        "grazing_frequency_title": "ความถี่การกินตามโซนและปี",
        "grazing_impact_title": "ความสัมพันธ์ระหว่างการกินและการคลุมหญ้าทะเล",
        "grazing_zone_label": "โซน",
        "grazing_y_label": "ความถี่ / จำนวน",
        "x_year": "ปี",
        "y_percent_cover": "% การคลุม",
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