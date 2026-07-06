import streamlit as st
import os,sys


sys.path.append(os.path.join(os.path.dirname("Dashboard"), '..'))
st.set_page_config(
    page_title="I-SEM Market Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

st.title("I-SEM Market Dashboard")
st.markdown("""
This dashboard provides a quick look into the Irish Single Electricity Market (I-SEM). 

You can use the sidebar to jump between different views: checking recent prices, estimating thermal plant margins, or looking at system demand and wind generation.

- **Market Overview**: High-level KPIs and trends.
- **Price Analysis**: Deep dive into SMP and imbalance prices.
- **Bidding Economics**: Explore spark spreads and margins based on user-defined inputs.
- **Grid & System**: Analyze wind penetration, demand, and interconnectors.
- **Methodology**: Understand how this data is fetched and validated.
""")
