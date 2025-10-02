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
        df = pd.read_excel(path)
    except Exception as e:
        st.error(f"Failed to read transect file {os.path.basename(path)}: {e}")
        return pd.DataFrame()
    return df

def format_float(val):
    # Shows 2 decimals except if .00, then shows integer
    if pd.isnull(val):
        return ""
    val_rounded = round(val, 2)
    if val_rounded == int(val_rounded):
        return str(int(val_rounded))
    return f"{val_rounded:.2f}"

def main():
    df = load_data()

    # -------- Filter selection (always at the top) -----------
    st.title(t("title_zones"))

    col1, col2, col3 = st.columns(3)
    with col1:
        zones = sorted([z for z in df.dropna(subset=['ZONE'])["ZONE"].unique() if pd.notnull(z)])
        zone_sel = st.multiselect(t("nav_seagrass_zones"), zones, default=zones)
    with col2:
        mois = sorted(df.dropna(subset=['MONTH'])["MONTH"].astype(str).unique())
        mois_sel = st.multiselect(t("select_months"), mois, default=mois)
    with col3:
        annees = sorted(df.dropna(subset=['YEAR'])["YEAR"].astype(int).unique())
        annees_sel = st.multiselect("Years:", annees, default=annees)

    # -------- Tabs for figures --------
    tab1, tab2, tab3 = st.tabs([
        t("tab_species_zone"),
        t("tab_species_month"),
        t("tab_seagrass_cover")
    ])

    # -------- Prepare filtered data ----------- 
    df_rich = df.dropna(subset=['SP_RICHNESS', 'ZONE', 'MONTH', 'YEAR']).copy()
    df_rich["ZONE"] = pd.to_numeric(df_rich["ZONE"], errors='coerce')
    df_rich["YEAR"] = pd.to_numeric(df_rich["YEAR"], errors='coerce')
    df_rich["MONTH"] = df_rich["MONTH"].astype(str)
    df_rich["SP_RICHNESS"] = pd.to_numeric(df_rich["SP_RICHNESS"], errors='coerce')

    df_rich_filt = df_rich[
        (df_rich['ZONE'].isin(zone_sel)) &
        (df_rich['MONTH'].isin(mois_sel)) &
        (df_rich['YEAR'].isin(annees_sel))
    ]

    if df_rich_filt.empty:
        st.warning(t("no_species_data"))
    else:
        with tab1:
            st.header(t("avg_species_by_zone_title"))
            zone_stats = df_rich_filt.groupby('ZONE').agg(
                mean=('SP_RICHNESS', 'mean'),
                std_error=('SP_RICHNESS', lambda x: x.std(ddof=1) / np.sqrt(len(x))),
                count=('SP_RICHNESS', 'count')
            ).reset_index()
            fig_zone = px.bar(
                zone_stats,
                x='ZONE', y='mean',
                error_y='std_error',
                text=zone_stats['mean'].apply(format_float),
                labels={"mean": t("avg_species_y_label"), "ZONE": t("zone_x_label")},
                title=t("species_by_zone_chart_title")
            )
            fig_zone.update_yaxes(tickformat=".2f")
            # Display only the chart (removed side table)
            st.plotly_chart(fig_zone, use_container_width=True)

        with tab2:
            st.header(t("tab_species_month"))
            sel_par_zone = st.checkbox(t("show_by_zone"), value=False, key="sp_month")
            if sel_par_zone:
                mois_stats = df_rich_filt.groupby(['MONTH', 'ZONE']).agg(
                    mean=('SP_RICHNESS', 'mean'),
                    std_error=('SP_RICHNESS', lambda x: x.std(ddof=1) / np.sqrt(len(x)))
                ).reset_index()
                fig_mois = px.line(
                    mois_stats, x='MONTH', y='mean', error_y='std_error',
                    color='ZONE', markers=True,
                    labels={"mean": "Species Richness", "MONTH": "Month"},
                    title="Monthly Evolution by Zone"
                )
            else:
                mois_stats = df_rich_filt.groupby('MONTH').agg(
                    mean=('SP_RICHNESS', 'mean'),
                    std_error=('SP_RICHNESS', lambda x: x.std(ddof=1) / np.sqrt(len(x)))
                ).reset_index()
                fig_mois = px.line(
                    mois_stats, x='MONTH', y='mean', error_y='std_error',
                    markers=True,
                    labels={"mean": t("avg_species_y_label"), "MONTH": t("month_x_label")},
                    title=t("avg_species_by_month_title")
                )
                fig_mois.update_yaxes(tickformat=".2f")
                # Force a consistent height and margins so charts align vertically
                fig_mois.update_layout(height=420, margin=dict(t=60, b=40, l=60, r=20))

            c3, c4 = st.columns([3,2])
            with c3:
                st.plotly_chart(fig_mois, use_container_width=True)

            with c4:
                # small monthly bar chart
                fig_bar = px.bar(
                    mois_stats,
                    x='MONTH',
                    y='mean',
                    error_y='std_error',
                    text=mois_stats['mean'].apply(format_float),
                    labels={"mean": t("avg_species_y_label"), "MONTH": t("month_x_label")},
                    title=t("avg_species_by_month_title"),
                    color='mean',
                    color_continuous_scale='Viridis'
                )
                fig_bar.update_traces(marker_line_color='black', marker_line_width=1.5, textposition='outside')
                fig_bar.update_layout(
                    yaxis=dict(tickformat=".2f"),
                    xaxis_title=t("month_x_label"),
                    yaxis_title=t("avg_species_y_label"),
                    plot_bgcolor='rgba(245,245,245,1)',
                    bargap=0.3,
                    showlegend=False,
                    height=420,
                    margin=dict(t=110, b=40, l=40, r=20),
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # ---------------------------
            # Same charts but using MAX SP_RICHNESS per month
            # ---------------------------
            mois_stats_max = df_rich_filt.groupby('MONTH').agg(
                max_val=('SP_RICHNESS', 'max'),
                std_error=('SP_RICHNESS', lambda x: x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0)
            ).reset_index()

            # line chart for max
            fig_mois_max = px.line(
                mois_stats_max,
                x='MONTH',
                y='max_val',
                error_y='std_error',
                markers=True,
                labels={"max_val": t("avg_species_y_label"), "MONTH": t("month_x_label")},
                title=t("avg_species_by_month_title") + " (max)"
            )
            fig_mois_max.update_yaxes(tickformat=".2f")
            fig_mois_max.update_layout(height=420, margin=dict(t=60, b=40, l=60, r=20))

            # small bar chart for max
            fig_bar_max = px.bar(
                mois_stats_max,
                x='MONTH',
                y='max_val',
                error_y='std_error',
                text=mois_stats_max['max_val'].apply(format_float),
                labels={"max_val": t("avg_species_y_label"), "MONTH": t("month_x_label")},
                title=t("avg_species_by_month_title") + " (max)",
                color='max_val',
                color_continuous_scale='Viridis'
            )
            fig_bar_max.update_traces(marker_line_color='black', marker_line_width=1.5, textposition='outside')
            fig_bar_max.update_layout(
                yaxis=dict(tickformat=".2f"),
                xaxis_title=t("month_x_label"),
                yaxis_title=t("avg_species_y_label"),
                plot_bgcolor='rgba(245,245,245,1)',
                bargap=0.3,
                showlegend=False,
                height=420,
                margin=dict(t=110, b=40, l=40, r=20),
            )

            c5, c6 = st.columns([3,2])
            with c5:
                st.plotly_chart(fig_mois_max, use_container_width=True)
            with c6:
                st.plotly_chart(fig_bar_max, use_container_width=True)

            # Global stat
            st.subheader(t("global_species_richness"))
            global_stats = df_rich_filt["SP_RICHNESS"].agg(['mean', 'std', 'count'])
            global_mean = global_stats['mean']
            global_stderr = global_stats['std'] / np.sqrt(global_stats['count']) if global_stats['count'] > 0 else np.nan
            st.write(f"**{t('global_species_richness')}** {global_mean:.2f} ± {global_stderr:.2f} (n={global_stats['count']})")

            # Export
            csv = df_rich_filt.to_csv(index=False).encode('utf-8')
            st.download_button(label=t("download_filtered_data"), data=csv, file_name='filtered_species_richness.csv', mime='text/csv')

    # --------- Seagrass cover ----------- 
    with tab3:
        st.header(t("tab_seagrass_cover"))
        df_cov = df.copy()
        df_cov['ZONE'] = pd.to_numeric(df_cov['ZONE'], errors='coerce')
        df_cov['SEAGRASS_COVER'] = pd.to_numeric(df_cov['SEAGRASS_COVER'], errors='coerce')
        df_cov['YEAR'] = pd.to_numeric(df_cov['YEAR'], errors='coerce')
        df_cov['MONTH'] = df_cov['MONTH'].astype(str)
        df_cov = df_cov.dropna(subset=['ZONE', 'SEAGRASS_COVER', 'YEAR', 'MONTH'])
        df_cov_filt = df_cov[
            df_cov['ZONE'].isin(zone_sel) &
            df_cov['MONTH'].isin(mois_sel) &
            df_cov['YEAR'].isin(annees_sel)
        ]

        if df_cov_filt.empty:
            st.warning(t("no_cover_data"))
        else:
            stats = []
            for zone in sorted(df_cov_filt['ZONE'].unique()):
                covers = df_cov_filt[df_cov_filt['ZONE'] == zone]['SEAGRASS_COVER']
                mean = covers.mean()
                std_err = covers.std(ddof=1) / np.sqrt(len(covers)) if len(covers) > 0 else np.nan
                stats.append((f"Zone {int(zone)}", mean, std_err))
            fig = go.Figure()
            for (zone_name, mean, std_err) in stats:
                fig.add_trace(go.Bar(
                    x=[zone_name],
                    y=[mean],
                    name=zone_name,
                    error_y=dict(type='data', array=[std_err], visible=True),
                    text=[f"{mean:.2f} ± {std_err:.2f}"],
                    textposition='outside',
                    marker_color='green'
                ))
            if stats:
                try:
                    ymax = max([x[1] + (x[2] if not np.isnan(x[2]) else 0) + 5 for x in stats])
                except Exception:
                    ymax = 100
            else:
                ymax = 100
            fig.update_layout(
                title=t("seagrass_cover_comparison_title").format(months=", ".join(mois_sel), years=", ".join([str(y) for y in annees_sel])),
                xaxis_title=t("zone_x_label"),
                yaxis_title=t("percent_cover_y_label"),
                yaxis=dict(range=[0, ymax]),
                bargap=0.5,
                showlegend=False,
                height=600
            )
            # Display only the chart (removed side table)
            st.plotly_chart(fig, use_container_width=True)
