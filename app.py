import streamlit as st
import pandas as pd

st.set_page_config(page_title="Global Sustainability Dashboard", page_icon="🌍", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/wdi_sustainability.csv')
    return df

def main():
    st.title("🌍 Global Sustainability Dashboard")
    st.write("Exploring World Development Indicators on Sustainability")
    df = load_data()
    st.write(f"Loaded {len(df)} records")

if __name__ == "__main__":
    main()
