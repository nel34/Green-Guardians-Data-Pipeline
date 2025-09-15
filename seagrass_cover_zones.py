import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_excel('TRANSECT_DATA_SUMMARY.xlsx', sheet_name='TRANSECT DATA SUMMARY')
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
    st.title("🌱 Seagrass Meadows Exploration (Species Richness & Cover)")

    st.markdown("### Data Selection")
    col1, col2, col3 = st.columns(3)
    with col1:
        zones = sorted([z for z in df.dropna(subset=['ZONE'])["ZONE"].unique() if pd.notnull(z)])
        zone_sel = st.multiselect("Zones:", zones, default=zones)
    with col2:
        mois = sorted(df.dropna(subset=['MONTH'])["MONTH"].astype(str).unique())
        mois_sel = st.multiselect("Months:", mois, default=mois)
    with col3:
        annees = sorted(df.dropna(subset=['YEAR'])["YEAR"].astype(int).unique())
        annees_sel = st.multiselect("Years:", annees, default=annees)

    # -------- Tabs for figures --------
    tab1, tab2, tab3 = st.tabs([
        "Species Richness by Zone",
        "Species Richness by Month",
        "Seagrass Cover"
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
        st.warning("No species richness data for this selection.")
    else:
        with tab1:
            st.header("Average Species Richness by Zone")
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
                labels={"mean": "Average Species Richness", "ZONE": "Zone"},
                title='Species Richness by Zone'
            )
            fig_zone.update_yaxes(tickformat=".2f")
            # Display only the chart (removed side table)
            st.plotly_chart(fig_zone, use_container_width=True)

        with tab2:
            st.header("Species Richness by Month")
            sel_par_zone = st.checkbox("Show by zone", value=False, key="sp_month")
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
                    labels={"mean": "Species Richness", "MONTH": "Month"},
                    title="Monthly Evolution (All Zones)"
                )
            fig_mois.update_yaxes(tickformat=".2f")
            c3, c4 = st.columns([3,2])
            with c3:
                st.plotly_chart(fig_mois, use_container_width=True)
            with c4:
                mois_stats_fmt = mois_stats.copy()
                mois_stats_fmt['mean'] = mois_stats_fmt['mean'].apply(format_float)
                mois_stats_fmt['std_error'] = mois_stats_fmt['std_error'].apply(format_float)

                # New stylized bar chart to replace the table
                fig_bar = px.bar(
                    mois_stats,
                    x='MONTH',
                    y='mean',
                    error_y='std_error',
                    text=mois_stats['mean'].apply(format_float),
                    labels={"mean": "Average Species Richness", "MONTH": "Month"},
                    title="Average Species Richness by Month",
                    color='mean',
                    color_continuous_scale='Viridis'
                )
                fig_bar.update_traces(marker_line_color='black', marker_line_width=1.5, textposition='outside')
                fig_bar.update_layout(
                    yaxis=dict(tickformat=".2f"),
                    xaxis_title="Month",
                    yaxis_title="Average Species Richness",
                    plot_bgcolor='rgba(245,245,245,1)',
                    bargap=0.3,
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # Global stat
            st.subheader("Global Species Richness (all filters applied)")
            global_stats = df_rich_filt["SP_RICHNESS"].agg(['mean', 'std', 'count'])
            global_mean = global_stats['mean']
            global_stderr = global_stats['std'] / np.sqrt(global_stats['count']) if global_stats['count'] > 0 else np.nan
            st.write(f"**Global average species richness:** {global_mean:.2f} ± {global_stderr:.2f} (n={global_stats['count']})")

            # Export
            csv = df_rich_filt.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download filtered data (CSV)", data=csv, file_name='filtered_species_richness.csv', mime='text/csv')

    # --------- Seagrass cover ----------- 
    with tab3:
        st.header("Seagrass Cover Comparison")
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
            st.warning("No cover data for this selection.")
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
                title=f"Seagrass Cover Comparison by Zone ({', '.join(mois_sel)} - {', '.join([str(y) for y in annees_sel])})",
                xaxis_title="Zone",
                yaxis_title="% Cover",
                yaxis=dict(range=[0, ymax]),
                bargap=0.5,
                showlegend=False,
                height=600
            )
            # Display only the chart (removed side table)
            st.plotly_chart(fig, use_container_width=True)
