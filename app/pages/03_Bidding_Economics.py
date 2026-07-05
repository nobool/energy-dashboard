import streamlit as st
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.sidebar import render_sidebar

st.set_page_config(page_title="Bidding Economics", page_icon="🏭", layout="wide")
render_sidebar()
st.title("🏭 Bidding Economics (Spark Spread)")
st.markdown("Calculate spark spread and gross margin based on real-time market inputs.")

_, _, spark_df = load_data()

if spark_df.empty:
    st.warning("Data not available.")
else:
    st.sidebar.markdown("### 🎛️ Cost Assumptions")
    gas_price = st.sidebar.slider("Gas Price (€/MWh)", 10.0, 150.0, 30.0, step=1.0)
    carbon_price = st.sidebar.slider("Carbon Price (€/tonne)", 10.0, 150.0, 70.0, step=1.0)
    
    # SRMC = (Gas x HR) + (Carbon x EF) + VOM
    # Generic CCGT Assumptions: HR=2.0, EF=0.4, VOM=5.0
    srmc = (gas_price * 2.0) + (carbon_price * 0.4) + 5.0
    spark_df['Custom_SRMC'] = srmc
    spark_df['Custom_SparkSpread'] = spark_df['SMP'] - srmc
    
    st.metric("Live SRMC Estimate (CCGT)", f"€{srmc:.2f}/MWh")
    
    st.markdown("### Spark Spread (SMP - SRMC)")
    fig = px.line(spark_df, x='Datetime', y='Custom_SparkSpread', title='Estimated Spark Spread')
    fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Breakeven")
    st.plotly_chart(fig, use_container_width=True)
