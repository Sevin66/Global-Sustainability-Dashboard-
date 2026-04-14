import streamlit as st
import pandas as pd

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
    
    st.write(f"Showing {len(filtered_df)} records")
    st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
