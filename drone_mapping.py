import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_excel('TRANSECT_DATA_SUMMARY.xlsx', sheet_name='TRANSECT DATA SUMMARY')
    return df

def to_num(x):
    return pd.to_numeric(x, errors='coerce')

def normalize_month(s):
    return str(s).strip().upper()

def format_float(val):
    if pd.isnull(val):
        return ""
    v = round(float(val), 2)
    return str(int(v)) if v == int(v) else f"{v:.2f}"

def main():
    st.title("🛩️ Drone Mapping")
    st.markdown("Seagrass mapped surface from drone mapping, with filters by year and month, deduplicated per month to avoid double-counting repeated entries. Placeholders are ready for cyanobacteria and dugong feeding evidence charts when data becomes available.")

    df = load_data()

    # Ensure expected columns exist
    for col in ["YEAR", "MONTH", "SITE", "ZONE",
                "SURFACE SEAGRASS MAPPING",
                "CYANOBACTERIA EVIDENCE",
                "DUGONG FEEDING EVIDENCE MAPPING"]:
        if col not in df.columns:
            df[col] = np.nan

    # Normalize
    df["YEAR"] = to_num(df["YEAR"])
    df["MONTH"] = df["MONTH"].astype(str).map(normalize_month)
    df["ZONE"] = to_num(df["ZONE"])
    df["SURFACE SEAGRASS MAPPING"] = to_num(df["SURFACE SEAGRASS MAPPING"])
    df["CYANOBACTERIA EVIDENCE"] = to_num(df["CYANOBACTERIA EVIDENCE"])
    df["DUGONG FEEDING EVIDENCE MAPPING"] = to_num(df["DUGONG FEEDING EVIDENCE MAPPING"])

    # Filters
    months_order = ["JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE",
                    "JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"]
    years_available = sorted([int(y) for y in df["YEAR"].dropna().unique()])
    months_available = [m for m in months_order if m in df["MONTH"].dropna().unique()]

    col1, col2 = st.columns(2)
    with col1:
        years_sel = st.multiselect("Years:", years_available, default=years_available)
    with col2:
        months_sel = st.multiselect("Months:", months_available, default=months_available)

    df_filt = df[df["YEAR"].isin(years_sel) & df["MONTH"].isin(months_sel)].copy()

    # -----------------------------
    # Seagrass mapped surface chart
    # -----------------------------
    st.subheader("Seagrass mapped surface")
    st.caption("Each month is counted once even if multiple rows repeat the same surface. If multiple unique surfaces exist for the same month across sites/zones, they are summed.")

    df_surf = df_filt.dropna(subset=["SURFACE SEAGRASS MAPPING"]).copy()
    if df_surf.empty:
        st.info("No seagrass mapping data available for the current selection.")
    else:
        # Deduplicate repeated surfaces within the same Year/Month/Site/Zone
        subset_keys = [k for k in ["YEAR","MONTH","SITE","ZONE","SURFACE SEAGRASS MAPPING"] if k in df_surf.columns]
        df_unique = df_surf.drop_duplicates(subset=subset_keys)

        # Aggregate per Year-Month (sum unique surfaces across sites/zones for that month)
        surf_month = (
            df_unique.groupby(["YEAR","MONTH"], as_index=False)["SURFACE SEAGRASS MAPPING"].sum()
        )

        # Sort by chronological month order within year
        surf_month["MONTH"] = pd.Categorical(surf_month["MONTH"], categories=months_order, ordered=True)
        surf_month = surf_month.sort_values(["YEAR","MONTH"])

        fig = px.bar(
            surf_month,
            x="MONTH",
            y="SURFACE SEAGRASS MAPPING",
            color="YEAR",
            barmode="group",
            labels={
                "MONTH": "Month",
                "SURFACE SEAGRASS MAPPING": "Mapped surface (units)",
                "YEAR": "Year"
            },
            title="Mapped Seagrass Surface by Month and Year",
            text=surf_month["SURFACE SEAGRASS MAPPING"].apply(format_float)
        )
        fig.update_yaxes(tickformat=".2f")
        fig.update_traces(texttemplate="%{text}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

        # Table
        tbl = surf_month.copy()
        tbl["SURFACE SEAGRASS MAPPING"] = tbl["SURFACE SEAGRASS MAPPING"].apply(format_float)
        st.dataframe(tbl, use_container_width=True, hide_index=True)

    # --------------------------------
    # Cyanobacteria Evidence (ready)
    # --------------------------------
    st.subheader("Cyanobacteria evidence")
    df_cy = df_filt.dropna(subset=["CYANOBACTERIA EVIDENCE"]).copy()
    if df_cy.empty:
        st.info("No cyanobacteria evidence data yet. This chart will populate once data is added.")
    else:
        cy_keys = [k for k in ["YEAR","MONTH","SITE","ZONE","CYANOBACTERIA EVIDENCE"] if k in df_cy.columns]
        df_cy_u = df_cy.drop_duplicates(subset=cy_keys)
        cy_month = (
            df_cy_u.groupby(["YEAR","MONTH"], as_index=False)["CYANOBACTERIA EVIDENCE"].sum()
        )
        cy_month["MONTH"] = pd.Categorical(cy_month["MONTH"], categories=months_order, ordered=True)
        cy_month = cy_month.sort_values(["YEAR","MONTH"])

        fig_cy = px.bar(
            cy_month,
            x="MONTH",
            y="CYANOBACTERIA EVIDENCE",
            color="YEAR",
            barmode="group",
            labels={
                "MONTH":"Month",
                "CYANOBACTERIA EVIDENCE":"Cyanobacteria evidence (units)",
                "YEAR":"Year"
            },
            title="Cyanobacteria Evidence by Month and Year",
            text=cy_month["CYANOBACTERIA EVIDENCE"].apply(format_float)
        )
        fig_cy.update_yaxes(tickformat=".2f")
        fig_cy.update_traces(texttemplate="%{text}", textposition="outside")
        st.plotly_chart(fig_cy, use_container_width=True)
        st.dataframe(cy_month, use_container_width=True, hide_index=True)

    # -----------------------------------------------
    # Dugong Feeding Evidence Mapping (ready as well)
    # -----------------------------------------------
    st.subheader("Dugong feeding evidence mapping")
    df_dug = df_filt.dropna(subset=["DUGONG FEEDING EVIDENCE MAPPING"]).copy()
    if df_dug.empty:
        st.info("No dugong feeding evidence mapping data yet. This chart will populate once data is added.")
    else:
        dug_keys = [k for k in ["YEAR","MONTH","SITE","ZONE","DUGONG FEEDING EVIDENCE MAPPING"] if k in df_dug.columns]
        df_dug_u = df_dug.drop_duplicates(subset=dug_keys)
        dug_month = (
            df_dug_u.groupby(["YEAR","MONTH"], as_index=False)["DUGONG FEEDING EVIDENCE MAPPING"].sum()
        )
        dug_month["MONTH"] = pd.Categorical(dug_month["MONTH"], categories=months_order, ordered=True)
        dug_month = dug_month.sort_values(["YEAR","MONTH"])

        fig_dug = px.bar(
            dug_month,
            x="MONTH",
            y="DUGONG FEEDING EVIDENCE MAPPING",
            color="YEAR",
            barmode="group",
            labels={
                "MONTH":"Month",
                "DUGONG FEEDING EVIDENCE MAPPING":"Dugong feeding evidence (units)",
                "YEAR":"Year"
            },
            title="Dugong Feeding Evidence Mapping by Month and Year",
            text=dug_month["DUGONG FEEDING EVIDENCE MAPPING"].apply(format_float)
        )
        fig_dug.update_yaxes(tickformat=".2f")
        fig_dug.update_traces(texttemplate="%{text}", textposition="outside")
        st.plotly_chart(fig_dug, use_container_width=True)
        st.dataframe(dug_month, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
