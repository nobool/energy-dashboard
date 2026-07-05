import streamlit as st

st.set_page_config(
    page_title="I-SEM Market Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ I-SEM Market Dashboard")
st.markdown("""
Welcome to the I-SEM Market Dashboard. 
Use the sidebar to navigate through different analytical views of the Irish Single Electricity Market.

- **Market Overview**: High-level KPIs and trends.
- **Price Analysis**: Deep dive into SMP and imbalance prices.
- **Bidding Economics**: Explore spark spreads and margins based on user-defined inputs.
- **Grid & System**: Analyze wind penetration, demand, and interconnectors.
- **Methodology**: Understand how this data is fetched and validated.
""")
