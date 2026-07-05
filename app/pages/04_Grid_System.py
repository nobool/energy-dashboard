import streamlit as st
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.sidebar import render_sidebar

st.set_page_config(page_title="Grid & System", page_icon="🌐", layout="wide")
render_sidebar()
st.title("🌐 Grid & System Conditions")

_, grid_df, _ = load_data()

if grid_df.empty:
    st.warning("Data not available.")
else:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### CO2 Intensity Trend")
        if 'CO2Intensity' in grid_df.columns:
            fig = px.line(grid_df, x='Datetime', y='CO2Intensity', labels={'CO2Intensity':'CO2 Intensity (gCO2/kWh)'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("CO2 Intensity data not available.")
            
    with col2:
        st.markdown("### Interconnector Flows")
        if 'InterconnectorFlow' in grid_df.columns:
            fig2 = px.line(grid_df, x='Datetime', y='InterconnectorFlow', labels={'InterconnectorFlow':'Net Flow (MW)'})
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Interconnector flow data not available.")
