import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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

def format_float(val):
    if pd.isnull(val):
        return ""
    v = round(float(val), 2)
    return str(int(v)) if v == int(v) else f"{v:.2f}"

def main():
    df = load_data()

    df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
    df = df.dropna(subset=['YEAR'])
    df['YEAR'] = df['YEAR'].astype(int)

    st.title(t("title_seagrass"))

    years_available = sorted(df['YEAR'].unique())
    years_interest = st.multiselect(t("select_years"), years_available, default=years_available[:5])

    if not years_interest:
        st.warning(t("no_year_selected"))
        st.stop()

    df_filtered = df[df['YEAR'].isin(years_interest)]
    df_filtered['SEAGRASS_COVER'] = pd.to_numeric(df_filtered['SEAGRASS_COVER'], errors='coerce')

    stats = []
    for year in years_interest:
        covers = df_filtered[df_filtered['YEAR'] == year]['SEAGRASS_COVER'].dropna()
        mean = covers.mean()
        std_err = covers.std(ddof=1) / np.sqrt(len(covers)) if len(covers) > 0 else np.nan
        stats.append((year, mean, std_err, len(covers)))

    years = [str(s[0]) for s in stats]
    means = [s[1] for s in stats]
    errs = [s[2] for s in stats]
    ns = [s[3] for s in stats]

    # prepare texts for bar labels
    texts = [format_float(m) for m in means]

    fig = go.Figure()
    # Single uniform colour for all bars (no per-bar colours)
    uniform_color = "steelblue"
    fig.add_trace(go.Bar(
        x=years,
        y=means,
        error_y=dict(type='data', array=errs, visible=True, thickness=1.5, width=6),  # width>0 restores caps
        marker=dict(color=uniform_color, line=dict(width=1, color='rgba(0,0,0,0.08)')),
        text=texts,
        textposition='outside',
        hovertemplate=(
            "<b>Year</b>: %{x}<br>"
            "<b>Mean</b>: %{y:.2f}%<br>"
            "<b>Std err</b>: %{customdata[0]:.2f}<br>"
            "<b>n</b>: %{customdata[1]}<extra></extra>"
        ),
        customdata=np.column_stack((errs, ns)),
        showlegend=False
    ))

    fig.update_layout(
        title=t("chart_avg_cover"),
        xaxis_title=t("x_year"),
        yaxis_title=t("y_percent_cover"),
        template="plotly_white",
        bargap=0.25,
        yaxis=dict(range=[0, max([m + (e or 0) for m, e in zip(means, errs)]) * 1.08]),
        height=520
    )
    fig.update_traces(marker_line_color="rgba(0,0,0,0.08)", marker_line_width=1)

    result_table = pd.DataFrame(stats, columns=['Year', 'Mean (%)', "Standard Error", "n"])
    result_table['Year'] = result_table['Year'].astype(str)
    result_table['Mean (%)'] = result_table['Mean (%)'].apply(format_float)
    result_table['Standard Error'] = result_table['Standard Error'].apply(format_float)

    st.plotly_chart(fig, use_container_width=True)
        
    st.header(t("avg_by_month_header"))

    # Standardize month names
    df['MONTH'] = df['MONTH'].astype(str).str.upper()

    # Define chronological order for months
    month_order = [
        "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
        "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
    ]

    # List of available months dynamically, sorted chronologically
    months_available = [m for m in month_order if m in df['MONTH'].unique()]
    months_interest = st.multiselect(
        t("select_months"),
        months_available,
        default=months_available
    )

    # Ensure months_interest is in chronological order
    months_interest = [m for m in month_order if m in months_interest]

    # Filtrage
    df_months = df[
        (df['MONTH'].isin(months_interest)) &
        (df['YEAR'].isin(years_interest))
    ].copy()
    df_months['SEAGRASS_COVER'] = pd.to_numeric(df_months['SEAGRASS_COVER'], errors='coerce')
    df_months = df_months.dropna(subset=['SEAGRASS_COVER'])

    if df_months.empty:
        st.warning(t("no_month_data"))
    else:
        # Calculate means and standard errors
        month_stats = df_months.groupby('MONTH').agg(
            mean=('SEAGRASS_COVER', 'mean'),
            std_error=('SEAGRASS_COVER', lambda x: x.std(ddof=1) / np.sqrt(len(x)))
        ).reindex(months_interest).reset_index()

        # Build the chart
        fig_month = go.Figure()
        # month chart: uniform colour, single trace, show labels and caps
        month_texts = month_stats['mean'].apply(format_float).tolist()
        fig_month.add_trace(go.Bar(
            x=month_stats['MONTH'],
            y=month_stats['mean'],
            error_y=dict(type='data', array=month_stats['std_error'].fillna(0).tolist(), visible=True, thickness=1.5, width=6),  # caps restored
            marker=dict(color=uniform_color, line=dict(width=1, color='rgba(0,0,0,0.08)')),
            text=month_texts,
            textposition='outside',
            hovertemplate=(
                "<b>Month</b>: %{x}<br>"
                "<b>Mean</b>: %{y:.2f}%<br>"
                "<b>Std err</b>: %{customdata[0]:.2f}<extra></extra>"
            ),
            customdata=np.column_stack((month_stats['std_error'].fillna(0),)),
            showlegend=False
        ))

        fig_month.update_layout(
            title=t("chart_avg_cover_by_month"),
            xaxis_title=t("month_x_label"),
            yaxis_title=t("y_percent_cover"),
            yaxis=dict(range=[0, max(month_stats['mean'] + month_stats['std_error']) + 5]),
            bargap=0.5,
            showlegend=False,
            height=500
        )

        st.plotly_chart(fig_month, use_container_width=True)

if __name__ == "__main__":
    main()
