import streamlit as st
import pandas as pd
import os

def load_data():
    @st.cache_data
    def fetch_csv(path, mtime):
        # mtime is included in the cache key — when the file changes on disk
        # after a bot commit, its mtime changes, busting the cache automatically.
        df = pd.read_csv(path)
        if 'Datetime' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Datetime'])
        return df

    # Assuming app is run from energy-dashboard root
    data_dir = 'data'
    if not os.path.exists(data_dir):
        data_dir = '../data'

    def load(filename):
        path = os.path.join(data_dir, filename)
        return fetch_csv(path, os.path.getmtime(path))

    smp = load('smp_prices.csv')
    grid = load('eirgrid_grid.csv')
    spark = load('spark_spread.csv')

    return smp, grid, spark
