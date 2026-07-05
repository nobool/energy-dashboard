import streamlit as st
import sys
import os

# Add parent directory to path so we can import components
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.charts import plot_smp_timeseries, plot_demand_wind_area
from components.sidebar import render_sidebar

st.set_page_config(page_title="Market Overview", layout="wide")
render_sidebar()
st.title("Market Overview")

smp_df, grid_df, _ = load_data()

if smp_df.empty or grid_df.empty:
    st.warning("Data not available. Please ensure pipeline has generated data.")
else:
    col1, col2, col3, col4 = st.columns(4)
    latest_smp = smp_df.iloc[-1]['SMP'] if not smp_df.empty else 0
    latest_demand = grid_df.iloc[-1]['SystemDemand'] if not grid_df.empty else 0
    latest_wind = grid_df.iloc[-1]['WindGeneration'] if not grid_df.empty else 0
    wind_pct = (latest_wind / latest_demand) * 100 if latest_demand > 0 else 0
    
    col1.metric("Latest SMP (€/MWh)", f"€{latest_smp:.2f}")
    col2.metric("System Demand (MW)", f"{latest_demand:.0f}")
    col3.metric("Wind Generation (MW)", f"{latest_wind:.0f}")
    col4.metric("Wind Penetration (%)", f"{wind_pct:.1f}%")

    st.markdown("### SMP Trends")
    if not smp_df.empty:
        st.plotly_chart(plot_smp_timeseries(smp_df), use_container_width=True)

    st.markdown("### System Demand & Wind")
    if not grid_df.empty:
        st.plotly_chart(plot_demand_wind_area(grid_df), use_container_width=True)
