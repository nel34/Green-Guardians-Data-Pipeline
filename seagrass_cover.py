import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_excel('TRANSECT_DATA_SUMMARY.xlsx', sheet_name='TRANSECT DATA SUMMARY')
    return df

def main():
    df = load_data()

    df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
    df = df.dropna(subset=['YEAR'])
    df['YEAR'] = df['YEAR'].astype(int)

    st.title("🌿 Average Seagrass Cover")

    years_available = sorted(df['YEAR'].unique())
    years_interest = st.multiselect("Select years of interest:", years_available, default=years_available[:5])

    if not years_interest:
        st.warning("No year selected. Please select at least one year to display the data.")
        st.stop()

    df_filtered = df[df['YEAR'].isin(years_interest)]
    df_filtered['SEAGRASS_COVER'] = pd.to_numeric(df_filtered['SEAGRASS_COVER'], errors='coerce')

    stats = []
    for year in years_interest:
        covers = df_filtered[df_filtered['YEAR'] == year]['SEAGRASS_COVER'].dropna()
        mean = covers.mean()
        std_err = covers.std(ddof=1) / np.sqrt(len(covers)) if len(covers) > 0 else np.nan
        stats.append((year, mean, std_err, len(covers)))

    fig = go.Figure()
    def format_float(val):
        return f"{val:.2f}".rstrip('0').rstrip('.') if not np.isnan(val) else ""

    for (year, mean, std_err, n) in stats:
        fig.add_trace(go.Bar(
            x=[str(year)],
            y=[mean],
            name=str(year),
            error_y=dict(type='data', array=[std_err], visible=True),
            text=[f"{format_float(mean)} ± {format_float(std_err)}"],
            textposition='outside',
            marker_color='gray',
            opacity=0.8
        ))

    fig.update_layout(
        title="Average Seagrass Cover (%)",
        xaxis_title="Year",
        yaxis_title="% Cover",
        yaxis=dict(
            range=[0, max([x[1] + (x[2] if not np.isnan(x[2]) else 0) + 5 for x in stats])],
            tickformat=".2~f"
        ),
        bargap=0.5,
        showlegend=False,
        height=600
    )

    result_table = pd.DataFrame(stats, columns=['Year', 'Mean (%)', "Standard Error", "n"])
    result_table['Year'] = result_table['Year'].astype(str)
    result_table['Mean (%)'] = result_table['Mean (%)'].apply(format_float)
    result_table['Standard Error'] = result_table['Standard Error'].apply(format_float)

    st.plotly_chart(fig, use_container_width=True)
        
    st.header("🌾 Average Seagrass Cover by Month (Fig. 4)")

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
        "Select months:",
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
        st.warning("No data for the selected months.")
    else:
        # Calculate means and standard errors
        month_stats = df_months.groupby('MONTH').agg(
            mean=('SEAGRASS_COVER', 'mean'),
            std_error=('SEAGRASS_COVER', lambda x: x.std(ddof=1) / np.sqrt(len(x)))
        ).reindex(months_interest).reset_index()

        # Build the chart
        fig_month = go.Figure()
        for _, row in month_stats.iterrows():
            fig_month.add_trace(go.Bar(
                x=[row['MONTH']],
                y=[row['mean']],
                error_y=dict(type='data', array=[row['std_error']], visible=True),
                text=[f"{row['mean']:.2f} ± {row['std_error']:.2f}"],
                textposition='outside',
                marker_color='teal'
            ))

        fig_month.update_layout(
            title="Average % Seagrass Cover by Month",
            xaxis_title="Month",
            yaxis_title="% Cover",
            yaxis=dict(range=[0, max(month_stats['mean'] + month_stats['std_error']) + 5]),
            bargap=0.5,
            showlegend=False,
            height=500
        )

        st.plotly_chart(fig_month, use_container_width=True)

if __name__ == "__main__":
    main()
