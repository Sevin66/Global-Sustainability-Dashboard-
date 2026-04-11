"""
Data preprocessing script for the WDI Sustainability Dashboard.
Reads the large WDI CSV files and extracts only the sustainability
indicators we need, producing a smaller cleaned dataset.
"""

import pandas as pd
import os

# Define the indicators we want to analyse
INDICATORS = {
    'EG.FEC.RNEW.ZS': 'Renewable energy consumption (% of total final energy consumption)',
    'EG.ELC.ACCS.ZS': 'Access to electricity (% of population)',
    'EG.CFT.ACCS.ZS': 'Access to clean fuels and technologies for cooking (% of population)',
    'AG.LND.FRST.ZS': 'Forest area (% of land area)',
}

def load_and_filter_data():
    """Load WDI data and filter for our sustainability indicators."""
    
    # Path to raw data
    raw_data_path = os.path.join('WDI_CSV_2026_04_09', 'WDICSV.csv')
    country_path = os.path.join('WDI_CSV_2026_04_09', 'WDICountry.csv')
    
    print("Loading raw WDI data (this may take a moment)...")
    
    # Read the main data file
    df = pd.read_csv(raw_data_path, encoding='utf-8-sig')
    
    print(f"Raw data shape: {df.shape}")
    
    # Filter for our selected indicators only
    df = df[df['Indicator Code'].isin(INDICATORS.keys())]
    
    print(f"After indicator filter: {df.shape}")
    
    # Read country metadata to filter out aggregates
    countries = pd.read_csv(country_path, encoding='utf-8-sig')
    
    # Keep only entries that have a Region (these are actual countries, not aggregates)
    real_countries = countries[countries['Region'].notna() & (countries['Region'] != '')]
    country_codes = real_countries['Country Code'].tolist()
    
    # Filter data to only include real countries
    df = df[df['Country Code'].isin(country_codes)]
    
    print(f"After country filter (removing aggregates): {df.shape}")
    
    # Get year columns (they are numbers like 1960, 1961, etc.)
    year_cols = [col for col in df.columns if col.isdigit() or (isinstance(col, str) and col.replace('.', '').isdigit())]
    
    # Keep only years from 2000 onwards to reduce data size
    year_cols = [col for col in year_cols if int(float(col)) >= 2000]
    
    # Melt the dataframe from wide to long format
    id_cols = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
    df_long = df.melt(
        id_vars=id_cols,
        value_vars=year_cols,
        var_name='Year',
        value_name='Value'
    )
    
    # Convert Year to integer
    df_long['Year'] = df_long['Year'].astype(int)
    
    # Remove rows where Value is missing
    df_long = df_long.dropna(subset=['Value'])
    
    # Add Region column from country metadata
    region_map = real_countries.set_index('Country Code')['Region'].to_dict()
    income_map = real_countries.set_index('Country Code')['Income Group'].to_dict()
    
    df_long['Region'] = df_long['Country Code'].map(region_map)
    df_long['Income Group'] = df_long['Country Code'].map(income_map)
    
    # Sort by country and year
    df_long = df_long.sort_values(['Country Name', 'Indicator Code', 'Year'])
    
    # Reset index
    df_long = df_long.reset_index(drop=True)
    
    print(f"Final dataset shape: {df_long.shape}")
    print(f"Countries: {df_long['Country Name'].nunique()}")
    print(f"Indicators: {df_long['Indicator Code'].nunique()}")
    print(f"Year range: {df_long['Year'].min()} - {df_long['Year'].max()}")
    
    return df_long


def main():
    """Main function to run the preprocessing."""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Process the data
    df = load_and_filter_data()
    
    # Save to CSV
    output_path = os.path.join('data', 'wdi_sustainability.csv')
    df.to_csv(output_path, index=False)
    
    print(f"\nSaved cleaned dataset to {output_path}")
    print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")


if __name__ == '__main__':
    main()
