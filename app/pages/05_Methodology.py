import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.sidebar import render_sidebar

st.set_page_config(page_title="Methodology", layout="wide")
render_sidebar()
st.title("Methodology & Data Integrity")

st.markdown("""
Since the Integrated Single Electricity Market (ISEM) operates through a hierarchy: **Day-Ahead Market (DAM) > Intraday Market (IDM) > Balancing Market.**
Prices in the balancing market (Imbalance Settlement Price, ISP) are highly volatile and create opportunities 

### Data Sources
The data was pulled from a few different places to put this together:
- **SEMOpx**: Static reports API for SMP & ISP. (Used for SMP and Imbalance Settlement Prices)
- **EirGrid**: Smart Grid Dashboard API. (Used for System Demand, Wind Generation, CO2 Intensity, and Interconnector flows)
- **ENTSO-E**: Transparency Platform API. (Used for cross-validation of day-ahead prices, mostly as a sanity check against SEMOpx data)

### Validation Checks
To make sure the data isn't completely off, the following checks are in place
1. **Source Cross-Validation**: Compare SEMOpx SMP vs ENTSO-E IE_SEM day-ahead prices.
2. **Market Logic Checks**: 
   - Ensure wind penetration negatively correlates with SMP.
   - Flag anomalies (e.g., extreme negative pricing).


### Margin Calculation
For the bidding economics page, a fairly standard SRMC formula is used:
`SRMC = (Gas Price × Heat Rate) + (Carbon Price × Emission Factor) + VOM`

Looking at the Spark Spread (SMP - SRMC) helps identify hours where a gas plant (like a CCGT) is "in the money" and should ideally be generating or dispatched.
""");
