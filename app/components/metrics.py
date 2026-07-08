import streamlit as st
import pandas as pd
import os

def load_data():
    @st.cache_data
    def fetch_csv(path):
        df = pd.read_csv(path)
        if 'Datetime' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Datetime'])
        return df
            
    # Assuming app is run from energy-dashboard root
    data_dir = 'data'
    if not os.path.exists(data_dir):
        data_dir = '../data'
        
    smp = fetch_csv(os.path.join(data_dir, 'smp_prices.csv'))
    grid = fetch_csv(os.path.join(data_dir, 'eirgrid_grid.csv'))
    spark = fetch_csv(os.path.join(data_dir, 'spark_spread.csv'))
    
    return smp, grid, spark
