import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.sidebar import render_sidebar
from components.charts import plot_day_ahead_prices, plot_interconnector_flows_price_variance

st.set_page_config(page_title="Grid & System", layout="wide",page_icon="⚡")
render_sidebar()
from components.header import render_header
render_header("Grid & System Conditions")

smp_df, grid_df, _ = load_data()

if grid_df.empty or smp_df.empty:
    st.warning("Data not available.")
else:
    st.plotly_chart(plot_day_ahead_prices(smp_df), use_container_width=True)
    st.caption("*Note: Nord Pool N2EX was used as the GB Day-Ahead Price. The GB and Irish Day Ahead markets are no longer implicitly coupled post-Brexit.*")

    st.plotly_chart(plot_interconnector_flows_price_variance(smp_df, grid_df), use_container_width=True)