import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.sidebar import render_sidebar

st.set_page_config(page_title="Methodology", page_icon="📚", layout="wide")
render_sidebar()
st.title("📚 Methodology & Data Integrity")

st.markdown("""
### Section A — How I-SEM Works
The Integrated Single Electricity Market (I-SEM) operates through a hierarchy:
**Day-Ahead Market (DAM) > Intraday Market (IDM) > Balancing Market.**
Prices in the balancing market (Imbalance Settlement Price, ISP) are highly volatile and create opportunities for flexible assets to capture value through gross margin optimization.

### Section B — Data Sources
- **SEMOpx**: Static reports API for SMP & ISP. (Used for market pricing)
- **EirGrid**: Smart Grid Dashboard API. (Used for System Demand, Wind Generation, CO2 Intensity, and Interconnector flows)
- **ENTSO-E**: Transparency Platform API. (Used for cross-validation of day-ahead prices)

### Section C — 3-Layer Cross-Validation
To ensure data integrity, this dashboard pipeline employs a robust cross-validation approach:
1. **Source Cross-Validation**: Compare SEMOpx SMP vs ENTSO-E IE_SEM day-ahead prices.
2. **Market Logic Sanity Checks**: 
   - Ensure wind penetration negatively correlates with SMP.
   - Flag anomalies (e.g., extreme negative pricing).
3. **Published Report Benchmarks**: Cross-referencing aggregates with CRU Market Monitoring Reports and EirGrid Annual Renewable Reports.

### Section D — SRMC Methodology
Short Run Marginal Cost (SRMC) is a critical input for ex-ante bidding strategies. 
```text
SRMC = (Gas Price × Heat Rate) + (Carbon Price × Emission Factor) + VOM
```
- **Spark Spread Proxy**: `Spark Spread = SMP - SRMC`
- A positive spark spread indicates hours where a gas plant (like a CCGT) is "in the money" and should ideally be generating or dispatched.
""")
