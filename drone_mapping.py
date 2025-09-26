import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import translations
import os
import data_utils

t = translations.t

@st.cache_data
def load_data():
    path = data_utils.find_latest_transect_file(None)
    if path is None:
        st.error("No transect Excel file found (looking for 'TRANSECT DATA SUMMARY *.xlsx' in repo root or data/).")
        return pd.DataFrame()
    try:
        df = pd.read_excel(path)
    except Exception as e:
        st.error(f"Failed to read transect file {os.path.basename(path)}: {e}")
        return pd.DataFrame()
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
    st.title(t("title_drone"))

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
        years_sel = st.multiselect(t("x_year"), years_available, default=years_available)
    with col2:
        months_sel = st.multiselect(t("month_x_label"), months_available, default=months_available)

    df_filt = df[df["YEAR"].isin(years_sel) & df["MONTH"].isin(months_sel)].copy()

    # -----------------------------
    # Seagrass mapped surface chart (no UI controls)
    # -----------------------------
    st.subheader(t("seagrass_mapped_surface"))

    df_surf = df_filt.copy()
    df_surf["SURFACE SEAGRASS MAPPING"] = pd.to_numeric(df_surf["SURFACE SEAGRASS MAPPING"], errors="coerce")
    df_surf = df_surf.dropna(subset=["SURFACE SEAGRASS MAPPING"])

    if df_surf.empty:
        st.info(t("no_drone_data"))
    else:
        # Fixed parameters (no UI)
        min_keep = 0.0
        agg_choice = "max"  # other options: last_non_null, first_non_null, mode

        if min_keep > 0:
            df_surf = df_surf[df_surf["SURFACE SEAGRASS MAPPING"] >= min_keep]

        df_surf = df_surf.sort_index()

        def pick_month_value(g):
            vals = g["SURFACE SEAGRASS MAPPING"].dropna().astype(float).values
            if len(vals) == 0:
                return np.nan
            if agg_choice == "max":
                return float(np.max(vals))
            if agg_choice == "first_non_null":
                return float(vals)
            if agg_choice == "last_non_null":
                return float(vals[-1])
            if agg_choice == "mode":
                v, c = np.unique(vals, return_counts=True)
                return float(v[np.argmax(c)])
            return float(np.max(vals))

        surf_month = (
            df_surf.groupby(["YEAR","MONTH"], as_index=False)
                .apply(pick_month_value)
                .rename(columns={None: "SURFACE SEAGRASS MAPPING"})
        )

        surf_month["YEAR"] = surf_month["YEAR"].astype(int).astype(str)
        months_order = ["JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE",
                        "JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"]
        surf_month["MONTH"] = pd.Categorical(surf_month["MONTH"], categories=months_order, ordered=True)
        surf_month = surf_month.sort_values(["YEAR","MONTH"])

        fig = px.bar(
            surf_month,
            x="MONTH",
            y="SURFACE SEAGRASS MAPPING",
            color="YEAR",
            barmode="group",
            labels={
                "MONTH": t("month_x_label"),
                "SURFACE SEAGRASS MAPPING": t("mapped_surface_y_label"),
                "YEAR": t("x_year")
            },
            title=t("mapped_surface_title"),
            text=surf_month["SURFACE SEAGRASS MAPPING"].map(lambda v: "" if pd.isna(v) else f"{v:.2f}".rstrip('0').rstrip('.'))
        )
        fig.update_yaxes(tickformat=".2f")
        fig.update_traces(texttemplate="%{text}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

        tbl = surf_month.copy()
        tbl["SURFACE SEAGRASS MAPPING"] = tbl["SURFACE SEAGRASS MAPPING"].map(
            lambda v: "" if pd.isna(v) else f"{v:.2f}".rstrip('0').rstrip('.') + " m²"
        )
        tbl = tbl.rename(columns={"SURFACE SEAGRASS MAPPING": f"{t('mapped_surface_y_label')} (m²)"})
        st.dataframe(tbl, use_container_width=True, hide_index=True)

    # -----------------------------------------------
    # Dugong Feeding Evidence Mapping (ready as well)
    # -----------------------------------------------
    st.subheader(t("dugong_feeding_title"))
    df_dug = df_filt.dropna(subset=["DUGONG FEEDING EVIDENCE MAPPING"]).copy()
    if df_dug.empty:
        st.info(t("no_dugong_feeding"))
    else:
        dug_keys = [k for k in ["YEAR","MONTH","SITE","ZONE","DUGONG FEEDING EVIDENCE MAPPING"] if k in df_dug.columns]
        df_dug_u = df_dug.drop_duplicates(subset=dug_keys)
        dug_month = (
            df_dug_u.groupby(["YEAR","MONTH"], as_index=False)["DUGONG FEEDING EVIDENCE MAPPING"].sum()
        )
        # Ensure YEAR is shown without thousand separators
        dug_month["YEAR"] = dug_month["YEAR"].astype(int).astype(str)
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
