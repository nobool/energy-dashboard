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

st.set_page_config(page_title="Methodology", layout="wide")
render_sidebar()

st.title("Methodology & Data Integrity")

st.header("Section A — How I-SEM Works")
st.markdown("""
The Irish Single Electricity Market (I-SEM) operates through a hierarchy of markets:
- **Day-Ahead Market (DAM)**: The primary ex-ante market where the bulk of energy is traded. Generates the System Marginal Price (SMP) via a merit order stack.
- **Intraday Markets (IDM)**: Allows participants to adjust their positions closer to real-time (e.g., IDA1, IDA2, IDA3).
- **Balancing Market**: Settles the difference between a participant's ex-ante position and their actual generation or demand. Imbalance Settlement Price (ISP) applies here.
Interconnectors (like EWIC and Moyle) participate implicitly, adjusting flows based on price differentials between I-SEM and GB markets.
""")

st.header("Section B — Data Sources & Pipeline")
st.markdown("""
- **SEMOpx**: Provides SMP and IDA prices. Data is fetched via the SEM-O API. Granularity: 30-minute.
- **EirGrid Smart Grid Dashboard**: Provides System Demand, Wind Generation, and Interconnector flows. Granularity: 15-minute.
- **ENTSO-E Transparency Platform**: Used to pull cross-validation data for Day-Ahead Prices and Actual Load. Granularity: 60-minute.

The pipeline automatically runs daily top-ups or full backfills. It merges disparate timelines by interpolating and forward-filling missing segments. 
""")

st.header("Section C — 3-Layer Cross-Validation Methodology")
st.markdown("""
To ensure data integrity, a 3-layer cross-validation process runs automatically during the pipeline:
1. **Source Cross-Validation**: Compares primary SEMOpx/EirGrid data against independent ENTSO-E metrics.
2. **Market Logic Sanity Checks**: Assesses the data against expected physical market realities (e.g. wind correlation, seasonality, spike alignment).
3. **Published Report Benchmarks**: Compares aggregates against CRU Market Monitoring Reports.
""")

try:
    val_df = pd.read_csv(DATA_DIR / "validation_report.csv")
    st.dataframe(val_df, use_container_width=True)
except FileNotFoundError:
    st.warning("Validation report not found. Run the data pipeline first.")

st.header("Section D — SRMC Methodology")
st.markdown("""
The Short-Run Marginal Cost (SRMC) determines a thermal unit's position in the merit order.

**SRMC = (Gas Price × Heat Rate) + (Carbon Price × Emission Factor) + Variable O&M (VOM)**

*Worked Example (Tynagh CCGT):*
- **Heat Rate**: 7.5 GJ/MWh
- **Emission Factor**: 0.202 tCO2/MWh
- **VOM**: €3.00/MWh
- **Example Inputs**: Gas €30/MWh, Carbon €65/tonne
- **SRMC** = (€30 × 7.5/2.6) + (€65 × 0.202) + €3.00 = ~€102.66/MWh  *(Note: GJ to MWh conversion applies to gas depending on units)*

The **Spark Spread** (SMP - SRMC) represents the gross margin opportunity for a gas plant. It acts as a primary signal for assessing ex-ante profitability and framing balancing market dispatch decisions.
""")
