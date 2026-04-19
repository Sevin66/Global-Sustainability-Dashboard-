import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Sustainability Dashboard", page_icon="🌍", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('data/wdi_sustainability.csv')

def get_indicator_label(code):
    labels = {'EG.FEC.RNEW.ZS': 'Renewable Energy (%)', 'EG.ELC.ACCS.ZS': 'Access to Electricity (%)', 'EG.CFT.ACCS.ZS': 'Clean Fuels Access (%)', 'AG.LND.FRST.ZS': 'Forest Area (%)'}
    return labels.get(code, code)

def main():
    df = load_data()
    st.title("🌍 Global Sustainability Dashboard")
    st.sidebar.header("🔧 Filters")
    indicator_options = df['Indicator Code'].unique().tolist()
    selected_indicator = st.sidebar.selectbox("Select Indicator", options=indicator_options, format_func=get_indicator_label)
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    year_range = st.sidebar.slider("Year Range", min_year, max_year, (2000, max_year))
    all_regions = sorted(df['Region'].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect("Select Regions", all_regions, default=all_regions)
    available_countries = sorted(df[df['Region'].isin(selected_regions)]['Country Name'].unique().tolist())
    selected_countries = st.sidebar.multiselect("Select Countries", available_countries, default=[])

    filtered_df = df[(df['Indicator Code'] == selected_indicator) & (df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1]) & (df['Region'].isin(selected_regions))]
    if selected_countries:
        filtered_df = filtered_df[filtered_df['Country Name'].isin(selected_countries)]
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Trends Over Time", "🌎 Regional Comparison", "🔀 Country Comparison", "📋 Data Explorer"])
    with tab1:
        st.subheader("Overview")
        if not filtered_df.empty:
            latest_year = filtered_df['Year'].max()
            compare_year = latest_year - 5
            latest_data = filtered_df[filtered_df['Year'] == latest_year]
            compare_data = filtered_df[filtered_df['Year'] == compare_year]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                avg_latest = latest_data['Value'].mean()
                st.metric("Global Average", f"{avg_latest:.1f}%")
            with col2:
                max_row = latest_data.loc[latest_data['Value'].idxmax()]
                st.metric("Highest", f"{max_row['Value']:.1f}%", max_row['Country Name'])
            with col3:
                min_row = latest_data.loc[latest_data['Value'].idxmin()]
                st.metric("Lowest", f"{min_row['Value']:.1f}%", min_row['Country Name'])
            with col4:
                st.metric("Countries", latest_data['Country Name'].nunique())

    with tab2:
        st.subheader("Trends Over Time")
        if not filtered_df.empty:
            fig_line = px.line(filtered_df, x='Year', y='Value', color='Country Name', markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.subheader("Regional Comparison")
        if not filtered_df.empty:
            year_data = filtered_df[filtered_df['Year'] == filtered_df['Year'].max()]
            region_avg = year_data.groupby('Region')['Value'].mean().reset_index()
            fig_bar = px.bar(region_avg, x='Value', y='Region', orientation='h')
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab4:
        st.subheader("Country Comparison")
        st.write("Select two indicators to compare across countries")

    with tab5:
        st.subheader("Data Explorer")
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
