import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.sidebar import render_sidebar

st.set_page_config(page_title="Grid & System", layout="wide",page_icon="⚡")
render_sidebar()
from components.header import render_header
render_header("Grid & System Conditions")

smp_df, grid_df, _ = load_data()

if grid_df.empty or smp_df.empty:
    st.warning("Data not available.")
else:
    st.markdown("### I-SEM vs GB Prices and Interconnector Flows")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'DAM_Price' in smp_df.columns:
        fig.add_trace(go.Scatter(x=smp_df['Datetime'], y=smp_df['DAM_Price'], name='I-SEM DAM Price'), secondary_y=False)
    if 'GB_DA_Price' in smp_df.columns:
        fig.add_trace(go.Scatter(x=smp_df['Datetime'], y=smp_df['GB_DA_Price'], name='GB DA Price'), secondary_y=False)
        
    if 'InterconnectorFlow' in grid_df.columns:
        fig.add_trace(go.Scatter(x=grid_df['Datetime'], y=grid_df['InterconnectorFlow'], name='Net Flow (MW)'), secondary_y=True)
        
    fig.update_layout(
        xaxis_title="Date",
        hovermode="x unified"
    )
    
    fig.update_yaxes(title_text="Price (€/MWh)", secondary_y=False)
    fig.update_yaxes(title_text="Net Flow (MW)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("*Note: Nord Pool N2EX was used as the GB Day-Ahead Price due to fairly small price variance compared to EPEX Spot. A single source was chosen since the markets are no longer implicitly coupled post-Brexit.*")
