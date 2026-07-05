import streamlit as st
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.sidebar import render_sidebar

st.set_page_config(page_title="Price Analysis", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Price Analysis")

smp_df, _, _ = load_data()

if smp_df.empty:
    st.warning("Data not available.")
else:
    smp_df['Hour'] = smp_df['Datetime'].dt.hour
    smp_df['DayOfWeek'] = smp_df['Datetime'].dt.day_name()
    
    heatmap_data = smp_df.groupby(['DayOfWeek', 'Hour'])['SMP'].mean().reset_index()
    
    st.markdown("### Average SMP by Hour and Day")
    fig = px.density_heatmap(heatmap_data, x='Hour', y='DayOfWeek', z='SMP', histfunc='avg', color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Imbalance Price Spread (SMP vs ISP)")
    if 'ISP' in smp_df.columns:
        fig2 = px.scatter(smp_df, x='Datetime', y=['SMP', 'ISP'], title='SMP vs Imbalance Settlement Price (ISP)')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("ISP data not available for spread analysis.")
