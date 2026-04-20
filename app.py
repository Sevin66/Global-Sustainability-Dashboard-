"""
WDI Sustainability Dashboard
An interactive dashboard to explore World Development Indicators
related to global sustainability.

Dataset: World Development Indicators (WDI) - The World Bank
Source: https://data360.worldbank.org/
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="Global Sustainability Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────
# Hide the deploy button to keep the UI clean
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2E86AB;
        text-align: center;
        padding: 0.5rem 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        text-align: center;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load the preprocessed sustainability dataset."""
    df = pd.read_csv('data/wdi_sustainability.csv')
    return df

def get_indicator_label(code):
    """Return a short label for each indicator code."""
    labels = {
        'EG.FEC.RNEW.ZS': 'Renewable Energy (%)',
        'EG.ELC.ACCS.ZS': 'Access to Electricity (%)',
        'EG.CFT.ACCS.ZS': 'Clean Fuels Access (%)',
        'AG.LND.FRST.ZS': 'Forest Area (%)',
    }
    return labels.get(code, code)

def main():
    """Main function to run the dashboard."""
    df = load_data()

    # ── Header ──────────────────────────────────────────────────────
    st.markdown('<div class="main-header">🌍 Global Sustainability Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Exploring World Development Indicators on Renewable Energy, '
        'Electricity Access, Clean Fuels, and Forest Coverage</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    # ── Sidebar Filters ─────────────────────────────────────────────
    st.sidebar.header("🔧 Filters")

    indicator_options = df['Indicator Code'].unique().tolist()
    selected_indicator = st.sidebar.selectbox(
        "Select Indicator",
        options=indicator_options,
        format_func=lambda x: get_indicator_label(x),
        index=0
    )

    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(2000, max_year),
        step=1
    )

    all_regions = sorted(df['Region'].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect(
        "Select Regions",
        options=all_regions,
        default=all_regions
    )

    available_countries = sorted(
        df[df['Region'].isin(selected_regions)]['Country Name'].unique().tolist()
    )
    selected_countries = st.sidebar.multiselect(
        "Select Countries (leave empty for all)",
        options=available_countries,
        default=[]
    )

    # ── Filter the Data ─────────────────────────────────────────────
    filtered_df = df[
        (df['Indicator Code'] == selected_indicator) &
        (df['Year'] >= year_range[0]) &
        (df['Year'] <= year_range[1]) &
        (df['Region'].isin(selected_regions))
    ]

    if selected_countries:
        filtered_df = filtered_df[filtered_df['Country Name'].isin(selected_countries)]

    # ── Tab Layout ──────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Trends Over Time", "🌎 Regional Comparison", "🔀 Country Comparison", "📋 Data Explorer"])

    # TAB 2: Overview - KPI Cards
    with tab2:
        st.subheader(f"Overview: {get_indicator_label(selected_indicator)}")

        if filtered_df.empty:
            st.warning("No data available for the selected filters.")
        else:
            latest_year = filtered_df['Year'].max()
            compare_year = latest_year - 5

            latest_data = filtered_df[filtered_df['Year'] == latest_year]
            compare_data = filtered_df[filtered_df['Year'] == compare_year]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                avg_latest = latest_data['Value'].mean()
                avg_compare = compare_data['Value'].mean() if not compare_data.empty else None
                delta = round(avg_latest - avg_compare, 2) if avg_compare else None
                st.metric(
                    label=f"Global Average ({latest_year})",
                    value=f"{avg_latest:.1f}%",
                    delta=f"{delta}% from {compare_year}" if delta else "N/A"
                )

            with col2:
                max_row = latest_data.loc[latest_data['Value'].idxmax()] if not latest_data.empty else None
                if max_row is not None:
                    st.metric(
                        label=f"Highest ({latest_year})",
                        value=f"{max_row['Value']:.1f}%",
                        delta=max_row['Country Name'],
                        delta_color="off"
                    )

            with col3:
                min_row = latest_data.loc[latest_data['Value'].idxmin()] if not latest_data.empty else None
                if min_row is not None:
                    st.metric(
                        label=f"Lowest ({latest_year})",
                        value=f"{min_row['Value']:.1f}%",
                        delta=min_row['Country Name'],
                        delta_color="off"
                    )

            with col4:
                num_countries = latest_data['Country Name'].nunique()
                st.metric(
                    label="Countries with Data",
                    value=num_countries,
                    delta=f"in {latest_year}",
                    delta_color="off"
                )

            st.markdown("---")
            st.subheader(f"Distribution by Region ({latest_year})")

            if not latest_data.empty:
                fig_box = px.box(
                    latest_data,
                    x='Region',
                    y='Value',
                    color='Region',
                    title=f'{get_indicator_label(selected_indicator)} Distribution by Region ({latest_year})',
                    labels={'Value': get_indicator_label(selected_indicator), 'Region': 'Region'},
                )
                fig_box.update_layout(showlegend=False, xaxis_tickangle=-45, height=450)
                st.plotly_chart(fig_box, use_container_width=True)

    # TAB 3: Trends Over Time
    with tab3:
        st.subheader(f"Trends Over Time: {get_indicator_label(selected_indicator)}")

        if filtered_df.empty:
            st.warning("No data available.")
        else:
            if not selected_countries:
                latest_year = filtered_df['Year'].max()
                top_countries = (
                    filtered_df[filtered_df['Year'] == latest_year]
                    .nlargest(5, 'Value')['Country Name']
                    .tolist()
                )
                trend_df = filtered_df[filtered_df['Country Name'].isin(top_countries)]
                st.info("Showing top 5 countries. Use the sidebar to select specific countries.")
            else:
                trend_df = filtered_df

            fig_line = px.line(
                trend_df,
                x='Year',
                y='Value',
                color='Country Name',
                title=f'{get_indicator_label(selected_indicator)} Over Time',
                labels={'Value': get_indicator_label(selected_indicator), 'Year': 'Year'},
                markers=True
            )
            fig_line.update_layout(hovermode='x unified', height=500, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
            st.plotly_chart(fig_line, use_container_width=True)

            st.subheader("Average Trend by Region")
            region_avg = filtered_df.groupby(['Year', 'Region'])['Value'].mean().reset_index()
            fig_region_trend = px.line(
                region_avg,
                x='Year',
                y='Value',
                color='Region',
                title=f'Regional Average: {get_indicator_label(selected_indicator)}',
                labels={'Value': f'Average {get_indicator_label(selected_indicator)}'},
                markers=True
            )
            fig_region_trend.update_layout(height=450)
            st.plotly_chart(fig_region_trend, use_container_width=True)

    # TAB 4: Regional Comparison
    with tab4:
        st.subheader(f"Regional Comparison: {get_indicator_label(selected_indicator)}")

        if filtered_df.empty:
            st.warning("No data available.")
        else:
            comparison_year = st.selectbox(
                "Select Year for Regional Comparison",
                options=sorted(filtered_df['Year'].unique(), reverse=True),
                index=0,
                key="region_year"
            )

            year_data = filtered_df[filtered_df['Year'] == comparison_year]

            if not year_data.empty:
                region_avg = year_data.groupby('Region')['Value'].mean().reset_index().sort_values('Value', ascending=True)
                fig_bar = px.bar(
                    region_avg,
                    x='Value',
                    y='Region',
                    orientation='h',
                    title=f'Average {get_indicator_label(selected_indicator)} by Region ({comparison_year})',
                    labels={'Value': get_indicator_label(selected_indicator)},
                    color='Value',
                    color_continuous_scale='Viridis'
                )
                fig_bar.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🔝 Top 10 Countries**")
                    top_10 = year_data.nlargest(10, 'Value')[['Country Name', 'Value', 'Region']].reset_index(drop=True)
                    top_10.index = top_10.index + 1
                    top_10.columns = ['Country', get_indicator_label(selected_indicator), 'Region']
                    st.dataframe(top_10, use_container_width=True)

                with col2:
                    st.markdown("**🔻 Bottom 10 Countries**")
                    bottom_10 = year_data.nsmallest(10, 'Value')[['Country Name', 'Value', 'Region']].reset_index(drop=True)
                    bottom_10.index = bottom_10.index + 1
                    bottom_10.columns = ['Country', get_indicator_label(selected_indicator), 'Region']
                    st.dataframe(bottom_10, use_container_width=True)

    # TAB 5: Country Comparison
    with tab5:
        st.subheader("Country Comparison: Two Indicators")
        all_indicators = df['Indicator Code'].unique().tolist()

        col1, col2 = st.columns(2)
        with col1:
            indicator_x = st.selectbox("X-Axis Indicator", options=all_indicators, format_func=get_indicator_label, index=0, key="scatter_x")
        with col2:
            indicator_y = st.selectbox("Y-Axis Indicator", options=all_indicators, format_func=get_indicator_label, index=1 if len(all_indicators) > 1 else 0, key="scatter_y")

        scatter_year = st.selectbox("Select Year", options=sorted(df['Year'].unique(), reverse=True), index=0, key="scatter_year")

        df_x = df[(df['Indicator Code'] == indicator_x) & (df['Year'] == scatter_year) & (df['Region'].isin(selected_regions))][['Country Name', 'Country Code', 'Value', 'Region']].rename(columns={'Value': 'X_Value'})
        df_y = df[(df['Indicator Code'] == indicator_y) & (df['Year'] == scatter_year) & (df['Region'].isin(selected_regions))][['Country Name', 'Country Code', 'Value']].rename(columns={'Value': 'Y_Value'})
        scatter_df = pd.merge(df_x, df_y, on=['Country Name', 'Country Code'], how='inner')

        if scatter_df.empty:
            st.warning("No data available.")
        else:
            fig_scatter = px.scatter(
                scatter_df,
                x='X_Value',
                y='Y_Value',
                color='Region',
                hover_name='Country Name',
                title=f'{get_indicator_label(indicator_x)} vs {get_indicator_label(indicator_y)} ({scatter_year})',
                labels={'X_Value': get_indicator_label(indicator_x), 'Y_Value': get_indicator_label(indicator_y)},
                size_max=15
            )
            fig_scatter.update_traces(marker=dict(size=10, opacity=0.7))
            fig_scatter.update_layout(height=550)
            st.plotly_chart(fig_scatter, use_container_width=True)

    # TAB 6: Data Explorer
    with tab6:
        st.subheader("📋 Data Explorer")
        if filtered_df.empty:
            st.warning("No data available.")
        else:
            st.markdown("**Summary Statistics**")
            summary = filtered_df['Value'].describe().round(2).to_frame().T
            st.dataframe(summary, use_container_width=True)

            st.markdown("**Filtered Data Table**")
            display_df = filtered_df[['Country Name', 'Region', 'Year', 'Value', 'Income Group']].copy()
            display_df.columns = ['Country', 'Region', 'Year', get_indicator_label(selected_indicator), 'Income Group']
            display_df = display_df.sort_values(['Country', 'Year']).reset_index(drop=True)
            st.dataframe(display_df, use_container_width=True, height=400)

            csv_data = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=csv_data,
                file_name=f"sustainability_data_{selected_indicator}.csv",
                mime="text/csv"
            )

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888; font-size: 0.85rem;'>"
        "Data Source: World Bank | 5DATA004C Coursework"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
