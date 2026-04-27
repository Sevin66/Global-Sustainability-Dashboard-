# Global Sustainability Dashboard

This is my project for the 5DATA004C Data Science Project Lifecycle module. It's an interactive Streamlit dashboard that looks at some sustainability metrics from the World Bank.

## The Data

I used the World Development Indicators (WDI) dataset from the World Bank. The raw data was downloaded via the "CSV Zip" link from the [World Bank Data Catalog](https://datacatalog.worldbank.org/infrastructure-data/search/dataset/0037712/world-development-indicators) and extracted into a local folder named `WDI_CSV_2026_04_09`.

**Note:** The raw data files are not included in this repository because of their large size.

The dashboard focuses on a few specific areas:
- Renewable energy consumption
- Access to electricity
- Access to clean fuels for cooking
- Forest area

The original dataset was huge (around 190MB), so I wrote a quick script (`data/preprocess.py`) to clean it up and only keep the specific indicators and actual countries I needed. The cleaned version (`wdi_sustainability.csv`) is included in this repository.

## What it does

The app has a few different sections:
- **Overview:** Basic stats and distribution charts
- **Trends:** Line charts to see how things changed over the years
- **Regional Comparison:** Bar charts comparing different regions
- **Country Comparison:** Scatter plots to see if two indicators correlate
- **Data:** A table where you can view the raw numbers and download them as a CSV

## Getting it running
 

1. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   streamlit run app.py
   ```

3. It should open automatically, but if not, just go to `http://localhost:8501` in your browser.

## Files in this repo

- `app.py`: The main dashboard code
- `data/preprocess.py`: Script to clean the raw data
- `data/wdi_sustainability.csv`: The cleaned data that the app actually uses
- `requirements.txt`: List of python packages you need
- `report.md`: My coursework report

Built with Python, Streamlit, Pandas, and Plotly.