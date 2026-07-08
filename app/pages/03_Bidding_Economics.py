import streamlit as st
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.sidebar import render_sidebar

st.set_page_config(page_title="Bidding Economics", layout="wide",page_icon="⚡")
render_sidebar()
from components.header import render_header
render_header("Bidding Economics (Spark Spread)")
st.write("Rough estimates for spark spread and plant margins.")

_, _, spark_df = load_data()

if spark_df.empty:
    st.warning("Data not available.")
else:
    st.sidebar.markdown("### Cost Assumptions")
    gas_price = st.sidebar.slider("Gas Price (€/MWh)", 10.0, 150.0, 30.0, step=1.0)
    carbon_price = st.sidebar.slider("Carbon Price (€/tonne)", 10.0, 150.0, 70.0, step=1.0)
    
    # SRMC = Fuel Cost + Carbon Cost + VOM
    ccgt_efficiency = 0.50
    heat_rate = 1 / ccgt_efficiency # MWh_th per MWh_e
    gas_emission_factor = 0.202 # tCO2 per MWh_th
    carbon_intensity = gas_emission_factor * heat_rate
    
    fuel_cost = gas_price * heat_rate
    carbon_cost = carbon_price * carbon_intensity
    srmc = fuel_cost + carbon_cost + 5.0
    spark_df['Custom_SRMC'] = srmc
    spark_df['Custom_SparkSpread'] = spark_df['DAM_Price'] - srmc
    
    st.metric("Live SRMC Estimate (CCGT)", f"€{srmc:.2f}/MWh")
    
    st.markdown("### Spark Spread (DAM Price - SRMC)")
    fig = px.line(spark_df, x='Datetime', y='Custom_SparkSpread', title='Estimated Spark Spread')
    fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Breakeven")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Margin Calculation")
st.markdown("""
Short Run Marginal Cost (SRMC) is a critical input for ex-ante bidding strategies. For our setup a fairly standard SRMC formula is used
```text
SRMC = (Gas Price × Heat Rate) + (Carbon Price × Emission Factor) + VOM
```
- **Spark Spread Proxy**: `Spark Spread = SMP - SRMC`
- A positive spark spread indicates hours where a gas plant (like a CCGT) is "in the money" and should ideally be generating or dispatched.
""")
