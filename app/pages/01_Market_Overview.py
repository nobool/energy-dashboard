import streamlit as st
import sys
import os

# Add parent directory to path so we can import components
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.charts import plot_market_prices, plot_system_demand_vs_renewables
from components.sidebar import render_sidebar

st.set_page_config(page_title="Market Overview", layout="wide",page_icon="⚡")
render_sidebar()
from components.header import render_header
render_header("Market Overview")

smp_df, grid_df, _ = load_data()

if smp_df.empty or grid_df.empty:
    st.warning("Data not available. Please ensure pipeline has generated data.")
else:
    def get_latest(df, col):
        return df.iloc[-1][col] if not df.empty and col in df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    latest_smp = get_latest(smp_df, 'DAM_Price')
    latest_demand = get_latest(grid_df, 'SystemDemand')
    latest_wind = get_latest(grid_df, 'WindGeneration')
    wind_pct = (latest_wind / latest_demand) * 100 if latest_demand > 0 else 0
    
    col1.metric("Latest DAM Price (€/MWh)", f"€{latest_smp:.2f}")
    col2.metric("System Demand (MW)", f"{latest_demand:.0f}")
    col3.metric("Wind Generation (MW)", f"{latest_wind:.0f}")
    col4.metric("Wind Penetration (%)", f"{wind_pct:.1f}%")

    st.markdown("### Market Price Trends")
    if not smp_df.empty:
        st.plotly_chart(plot_market_prices(smp_df), use_container_width=True)

    st.markdown("### System Demand vs Renewables")
    if not grid_df.empty:
        st.plotly_chart(plot_system_demand_vs_renewables(grid_df), use_container_width=True)
        st.caption("*Note: EirGrid system data is displayed here at its native 15-minute granularity to capture rapid system fluctuations. It is downsampled to 30-minute intervals in backend processing strictly when aligning with ex-ante market settlement periods.*")
