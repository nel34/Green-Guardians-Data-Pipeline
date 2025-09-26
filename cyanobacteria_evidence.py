import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
        df = pd.read_excel(path, sheet_name='TRANSECT DATA SUMMARY')
    except Exception as e:
        st.error(f"Failed to read transect file {os.path.basename(path)}: {e}")
        return pd.DataFrame()
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
        years_sel = st.multiselect(t("x_year"), years_available, default=years_available)
    with col2:
        months_sel = st.multiselect(t("month_x_label"), months_available, default=months_available)

    # Filter and prepare data
    df_filt = df[df["YEAR"].isin(years_sel) & df["MONTH"].isin(months_sel)].copy()
    df_filt["CYANOBACTERIA EVIDENCE"] = pd.to_numeric(df_filt["CYANOBACTERIA EVIDENCE"], errors="coerce")
    if df_filt.empty:
        st.info(t("no_cyano_data"))
        return

    # Deduplicate per relevant keys similar to original logic
    cy_keys = [k for k in ["YEAR","MONTH","SITE","ZONE","CYANOBACTERIA EVIDENCE"] if k in df_filt.columns]
    df_unique = df_filt.drop_duplicates(subset=cy_keys).copy()

    # convert to binary presence (1 if any record for that year/month indicates presence)
    df_unique["CYANOBACTERIA_PRESENT"] = pd.to_numeric(df_unique["CYANOBACTERIA EVIDENCE"], errors="coerce").fillna(0).gt(0).astype(int)
    cy_month = df_unique.groupby(["YEAR","MONTH"], as_index=False)["CYANOBACTERIA_PRESENT"].max()
    cy_month = cy_month.rename(columns={"CYANOBACTERIA_PRESENT": "CYANOBACTERIA EVIDENCE"})
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

    # -------------------------
    # Correlation: cyanobacteria presence vs mean seagrass cover
    # -------------------------
    if "SEAGRASS_COVER" in df.columns:
        # compute mean cover per YEAR/MONTH using the currently filtered dataframe (df_filt)
        cover = df_filt.copy()
        # ensure YEAR/MONTH normalized in the filtered frame
        cover["YEAR"] = pd.to_numeric(cover.get("YEAR", None), errors="coerce")
        cover["MONTH"] = cover.get("MONTH", "").astype(str).str.strip().str.upper()
        cover = cover[cover["YEAR"].notna() & cover["MONTH"].notna()].copy()
        if not cover.empty:
            cover_group = cover.groupby(["YEAR", "MONTH"], as_index=False)["SEAGRASS_COVER"].mean()
            cover_group["YEAR"] = cover_group["YEAR"].astype(int).astype(str)

            # merge presence (cy_month) with mean cover (keep months that have CYANO data)
            merged = pd.merge(
                cy_month[["YEAR", "MONTH", "CYANOBACTERIA EVIDENCE"]],
                cover_group,
                on=["YEAR", "MONTH"],
                how="left"   # keep months where we have cyanobacteria info even if cover missing
            )
            # ensure numeric
            merged["SEAGRASS_COVER"] = pd.to_numeric(merged.get("SEAGRASS_COVER"), errors="coerce")

            # --- try to fill missing SEAGRASS_COVER from the full dataset (not only df_filt) ---
            cover_all = df.copy()
            cover_all["YEAR"] = pd.to_numeric(cover_all.get("YEAR", None), errors="coerce")
            cover_all["MONTH"] = cover_all.get("MONTH", "").astype(str).str.strip().str.upper()
            cover_all = cover_all[cover_all["YEAR"].notna() & cover_all["MONTH"].notna()].copy()
            if "SEAGRASS_COVER" in cover_all.columns:
                cover_all_grp = cover_all.groupby(["YEAR", "MONTH"], as_index=False)["SEAGRASS_COVER"].mean()
                # normalize keys so dtypes match before merging
                cover_all_grp["YEAR"] = cover_all_grp["YEAR"].astype(int).astype(str)
                cover_all_grp["MONTH"] = cover_all_grp["MONTH"].astype(str).str.strip().str.upper()
                merged["YEAR"] = merged["YEAR"].astype(str)
                merged["MONTH"] = merged["MONTH"].astype(str).str.strip().str.upper()
                # merge alternative cover values (left join keeps cy_month rows)
                merged = merged.merge(cover_all_grp, on=["YEAR", "MONTH"], how="left", suffixes=("", "_alt"))
                # prefer existing, else take alt
                merged["SEAGRASS_COVER"] = merged["SEAGRASS_COVER"].fillna(merged.get("SEAGRASS_COVER_alt"))
                merged = merged.drop(columns=[c for c in merged.columns if c.endswith("_alt")])

            # --- if still missing, create a YM time index and interpolate across time (keeps chronology) ---
            merged["YEAR"] = pd.to_numeric(merged["YEAR"], errors="coerce").astype('Int64')
            merged["MONTH_TITLE"] = merged["MONTH"].str.strip().str.capitalize()
            merged["YM"] = pd.to_datetime(merged["YEAR"].astype(str) + "-" + merged["MONTH_TITLE"], format="%Y-%B", errors="coerce")
            merged = merged.sort_values("YM")
            if "SEAGRASS_COVER" in merged.columns:
                merged["SEAGRASS_COVER"] = merged["SEAGRASS_COVER"].interpolate(method="linear").ffill().bfill()
                # as last resort, fill remaining NA with 0
                merged["SEAGRASS_COVER"] = merged["SEAGRASS_COVER"].fillna(0)
            # drop helper cols if not needed later (but YM may be used)
            # merged.drop(columns=["MONTH_TITLE"], inplace=True)

            if merged.empty:
                st.info(t("no_cyano_data"))
            else:
                merged["presence_label"] = merged["CYANOBACTERIA EVIDENCE"].map({1: t("cyano_present_yes"), 0: t("cyano_present_no")})
                # bar chart removed (kept merged for the chronological line/area chart below)

                # build monthly aggregated view: mean cover and presence flag per month
                df_monthly = (
                    merged.groupby("MONTH", as_index=False)
                    .agg({"SEAGRASS_COVER": "mean", "CYANOBACTERIA EVIDENCE": "max"})
                )
                df_monthly["MONTH"] = pd.Categorical(df_monthly["MONTH"], categories=months_order, ordered=True)
                df_monthly = df_monthly.sort_values("MONTH")
                x = df_monthly["MONTH"].astype(str).tolist()
                y = df_monthly["SEAGRASS_COVER"].tolist()
                pres = df_monthly["CYANOBACTERIA EVIDENCE"].astype(int).tolist()

                # build two series: y_present (value when cyano present else 0) and y_absent (value when absent else 0)
                present_color = "rgba(255,99,71,0.35)"   # color when cyano present
                absent_color = "rgba(135,206,250,0.25)"  # color when absent

                y_present = [val if p == 1 else 0 for val, p in zip(y, pres)]
                y_absent = [val if p == 0 else 0 for val, p in zip(y, pres)]

                fig_line = go.Figure()
                # add absent area first (light color)
                fig_line.add_trace(
                    go.Scatter(
                        x=x,
                        y=y_absent,
                        mode="lines",
                        line=dict(width=0),
                        fill="tozeroy",
                        fillcolor=absent_color,
                        name=t("cyano_present_no"),
                        hoverinfo="x+y"
                    )
                )
                # add present area on top
                fig_line.add_trace(
                    go.Scatter(
                        x=x,
                        y=y_present,
                        mode="lines",
                        line=dict(width=0),
                        fill="tozeroy",
                        fillcolor=present_color,
                        name=t("cyano_present_yes"),
                        hoverinfo="x+y"
                    )
                )

                # overlay the mean cover line on top
                fig_line.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode="lines+markers",
                        line=dict(color="black", width=2),
                        name=t("chart_avg_cover"),
                        hovertemplate="%{x}<br>" + t("chart_avg_cover") + ": %{y:.2f}<extra></extra>",
                    )
                )

                fig_line.update_layout(
                    title=t("cyano_cover_correlation_title"),
                    xaxis_title=t("month_x_label"),
                    yaxis_title=t("chart_avg_cover"),
                    legend_title_text=t("cyano_presence_label"),
                    hovermode="x unified",
                    margin=dict(t=60, b=40, l=60, r=20),
                )
                fig_line.update_yaxes(tickformat=".2f")
                st.plotly_chart(fig_line, use_container_width=True)
    else:
        # colonne manquante -> rien à afficher
        pass

    st.dataframe(cy_month, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()