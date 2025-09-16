import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import translations
t = translations.t

@st.cache_data
def load_data():
    df = pd.read_excel('TRANSECT_DATA_SUMMARY.xlsx', sheet_name='TRANSECT DATA SUMMARY')
    return df

def format_float(val):
    if pd.isnull(val):
        return ""
    v = round(float(val), 2)
    return str(int(v)) if v == int(v) else f"{v:.2f}"

def main():
    st.title(t("title_cyano"))

    df = load_data()

    # Ensure columns exist
    if "CYANOBACTERIA EVIDENCE" not in df.columns:
        st.info(t("no_cyano_column"))
        return

    # Normalize
    df["YEAR"] = pd.to_numeric(df.get("YEAR", None), errors="coerce")
    df["MONTH"] = df.get("MONTH", "").astype(str).str.strip().str.upper()

    months_order = ["JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE",
                    "JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"]

    years_available = sorted([int(y) for y in df["YEAR"].dropna().unique()])
    months_available = [m for m in months_order if m in df["MONTH"].dropna().unique()]

    if not years_available:
        st.info("No year data available.")
        return

    col1, col2 = st.columns(2)
    with col1:
        years_sel = st.multiselect("Years:", years_available, default=years_available)
    with col2:
        months_sel = st.multiselect("Months:", months_available, default=months_available)

    # Filter and prepare data
    df_filt = df[df["YEAR"].isin(years_sel) & df["MONTH"].isin(months_sel)].copy()
    df_filt["CYANOBACTERIA EVIDENCE"] = pd.to_numeric(df_filt["CYANOBACTERIA EVIDENCE"], errors="coerce")
    if df_filt.empty:
        st.info(t("no_cyano_data"))
        return

    # Deduplicate per relevant keys similar to original logic
    cy_keys = [k for k in ["YEAR","MONTH","SITE","ZONE","CYANOBACTERIA EVIDENCE"] if k in df_filt.columns]
    df_unique = df_filt.drop_duplicates(subset=cy_keys)

    cy_month = df_unique.groupby(["YEAR","MONTH"], as_index=False)["CYANOBACTERIA EVIDENCE"].sum()
    cy_month["YEAR"] = cy_month["YEAR"].astype(int).astype(str)  # avoid thousand separators
    cy_month["MONTH"] = pd.Categorical(cy_month["MONTH"], categories=months_order, ordered=True)
    cy_month = cy_month.sort_values(["YEAR","MONTH"])

    fig = px.bar(
        cy_month,
        x="MONTH",
        y="CYANOBACTERIA EVIDENCE",
        color="YEAR",
        barmode="group",
        labels={
            "MONTH": t("month_x_label"),
            "CYANOBACTERIA EVIDENCE": t("cyano_y_label"),
            "YEAR": t("x_year")
        },
        title=t("cyano_chart_title"),
        text=cy_month["CYANOBACTERIA EVIDENCE"].apply(format_float)
    )
    fig.update_yaxes(tickformat=".2f")
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(cy_month, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()