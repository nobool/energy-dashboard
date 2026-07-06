import streamlit as st
import pandas as pd
import sys
import os

# Add app/ so we can import components
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Add energy-dashboard/ so we can import pipeline
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from components.sidebar import render_sidebar
from pipeline.config import DATA_DIR

st.set_page_config(page_title="Methodology", layout="wide",page_icon="⚡")
render_sidebar()

from components.header import render_header
render_header("Methodology & Data Integrity")

st.header("How I-SEM Works")
st.markdown("""
The Irish Single Electricity Market (I-SEM) operates through a hierarchy of markets:
- **Day-Ahead Market (DAM)**: The primary ex-ante market where the bulk of energy is traded. Generates the Day-Ahead Price via a merit order stack.
- **Intraday Markets (IDM)**: Allows participants to adjust their positions closer to real-time (e.g., IDA1, IDA2, IDA3).
- **Balancing Market**: Settles the difference between a participant's ex-ante position and actual generation or demand. The Imbalance Settlement Price (ISP) applies here.

Interconnectors (e.g., EWIC, Moyle, Greenlink) participate implicitly, adjusting flows based on price differentials between I-SEM and GB markets.
""")

st.header("Data Sources & Pipeline")
st.markdown("""
The dashboard relies on public APIs for market and system data:
- **SEMOpx**: Provides ex-ante market results via the EA-001 report (DAM, IDA1, IDA2, IDA3 prices and volumes).
- **SEM-O**: Provides balancing market data via the PUB_30MinAvgImbalPrc report (Imbalance Settlement Price and Net Imbalance Volume).
- **EirGrid**: Supplies real-time system metrics via the Smart Grid Dashboard (System Demand, Wind Generation, Solar Generation, CO2 Intensity, and Interconnector flows).
- **Nord Pool**: Provides Great Britain (GB) Day-Ahead prices (N2EX) for interconnector flow analysis.

The local data pipeline fetches, interpolates, and standardizes these inputs into unified datasets for visualization.
""")

st.header("Cross-Validation")
st.markdown("""
To maintain data integrity, the pipeline includes a foundational source-validation layer. It verifies primary SEMOpx and EirGrid data against independent ENTSO-E metrics. This specifically compares SEMOpx Day-Ahead Price against ENTSO-E Day-Ahead prices, and EirGrid Demand against ENTSO-E Actual Load to ensure basic source alignment.
""")

try:
    val_df = pd.read_csv(DATA_DIR / "validation_report.csv")
    st.dataframe(val_df, use_container_width=True)
except FileNotFoundError:
    st.warning("Validation report not found. Run the data pipeline first.")


